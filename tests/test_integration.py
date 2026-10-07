import ast
import re
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from auditlog.models import LogEntry
from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.template import engines
from django.template.loader import get_template
from django.test import RequestFactory, override_settings
from django.urls import resolve
from django_filters import rest_framework as filters
from rest_framework import generics, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.test import APIRequestFactory

from handyhelpers.drf_permissions import InAllGroups as ApiAllGroups
from handyhelpers.mixins.viewset_mixins import InvalidLookupMixin, PaginationControlMixin
from handyhelpers.querysets import count_by_week
from handyhelpers.templatetags.asset_tags import asset_manifest
from handyhelpers.views import gui, htmx, report
from tests.models import Category, Item, User

pytestmark = pytest.mark.django_db
TEMPLATES = Path("handyhelpers/templates")


def req(htmx_request=False):
    request = RequestFactory().get("/", HTTP_HX_REQUEST="true" if htmx_request else "false")
    request.user = AnonymousUser()
    request.resolver_match = resolve("/")
    return request


def test_all_templates_compile_and_literal_references_exist():
    for path in TEMPLATES.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text()
        get_template(str(path.relative_to(TEMPLATES)))
        assert "node_modules" not in text and "/bs4/" not in text
        for target in re.findall(r"""\{%\s*(?:include|extends)\s+["']([^"']+)""", text):
            assert (TEMPLATES / target).is_file(), (path, target)
        for target in re.findall(r"""\{%\s*static\s+["']([^"']+)""", text):
            assert (Path("handyhelpers/static") / target).is_file(), (path, target)


def test_every_builtin_literal_template_default_exists():
    for path in Path("handyhelpers").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and node.value.startswith("handyhelpers/")
                and node.value.endswith((".htm", ".html"))
            ):
                assert (TEMPLATES / node.value).is_file(), (path, node.value)


def test_default_pages_and_htmx_variants_render():
    for klass in [
        gui.HandyHelperIndexView,
        gui.HandyHelperActionView,
        gui.HandyHelperAboutView,
        htmx.HtmxItemizedView,
        report.AnnualStatView,
        report.AnnualTrendView,
        report.AnnualProgressView,
    ]:
        for partial in [False, True]:
            response = klass.as_view()(req(partial))
            assert response.status_code == 200, (klass, response)
    for klass in [gui.HandyHelperListView, gui.HandyHelperPaginatedListView]:
        response = klass.as_view(
            queryset=Item.objects.all(), table="handyhelpers/table/auditlog.htm"
        )(req())
        assert response.status_code == 200
    for klass, kwargs in [
        (htmx.BuildBootstrapModalView, {}),
        (htmx.HtmxSidebarItems, {"queryset": Item.objects.none()}),
        (htmx.BuildModelSidebarNav, {"menu_item_list": [{"queryset": Item.objects.none()}]}),
    ]:
        assert klass.as_view(**kwargs)(req(True)).status_code == 200


def test_sidebar_configuration_is_not_mutated():
    items = [{"queryset": Item.objects.all()}]
    response = htmx.BuildModelSidebarNav.as_view(menu_item_list=items)(req(True))
    assert response.status_code == 200 and "model_name" not in items[0]


def test_chart_json_escapes_script_terminators():
    template = engines["django"].from_string(
        "{% include 'handyhelpers/report/chartjs/bar_chart.htm' %}"
    )
    html = template.render(
        {
            "chart": {
                "id": "chart",
                "label_list": ["</script><script>alert(1)</script>"],
                "value_list": [1],
            }
        }
    )
    assert "</script><script>alert(1)" not in html
    assert "\\u003C" in html


def test_assets_are_pinned_with_integrity():
    assets = asset_manifest()
    assert len(assets) == 13
    for asset in assets.values():
        assert asset["url"].startswith("https://cdn.jsdelivr.net/npm/")
        assert re.search(r"@\d+\.\d+\.\d+/", asset["url"])
        assert asset["integrity"].startswith("sha384-")
    assert not Path("handyhelpers/static/node_modules").exists()


def test_auditlog_requires_target_permission_and_content_type(client):
    user = User.objects.create_user(username="audit-reader")
    item = Item.objects.create(name="Visible")
    content_type = ContentType.objects.get_for_model(Item)
    entry = LogEntry.objects.create(
        content_type=content_type,
        object_pk=str(item.pk),
        object_repr=str(item),
        action=LogEntry.Action.UPDATE,
        changes={"name": ["Old", "Visible"]},
    )
    list_url = f"/handyhelpers/get_auditlog_entries/tests/item/{item.pk}/"
    detail_url = f"/handyhelpers/get_auditlog_entry/{entry.pk}/"
    headers = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
    assert client.get(list_url, {"client_response": "yes"}, **headers).status_code == 302
    client.force_login(user)
    assert client.get(list_url, {"client_response": "yes"}, **headers).status_code == 403
    assert client.get(detail_url, {"client_response": "yes"}, **headers).status_code == 403
    user.user_permissions.add(
        Permission.objects.get(content_type=content_type, codename="view_item")
    )
    response = client.get(list_url, {"client_response": "yes"}, **headers)
    assert response.status_code == 200 and response["Content-Type"] == "application/json"
    assert "Visible" in response.json()["server_response"]
    detail = client.get(detail_url, {"client_response": "yes"}, **headers)
    assert detail.status_code == 200 and "Metadata" in detail.json()["server_response"]
    assert (
        client.get(
            "/handyhelpers/get_auditlog_entries/missing/item/1/",
            {"client_response": "yes"},
            **headers,
        ).status_code
        == 404
    )


def test_drf_filters_authentication_and_pagination():
    category = Category.objects.create(name="related")
    Item.objects.create(name="yes", category=category, number=1)

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = Item
            fields = ["id", "name"]

    class FilterSet(filters.FilterSet):
        category_name = filters.CharFilter(field_name="category__name")

        class Meta:
            model = Item
            fields = ["number"]

    class Page(PageNumberPagination):
        page_size = 1

    class Api(InvalidLookupMixin, PaginationControlMixin, generics.ListAPIView):
        queryset = Item.objects.order_by("pk")
        serializer_class = Serializer
        filterset_class = FilterSet
        pagination_class = Page
        permission_classes = [ApiAllGroups]
        permission_dict = {"GET": []}

    factory = APIRequestFactory()
    response = Api.as_view()(factory.get("/", {"category_name": "related"}))
    assert response.status_code == 200 and len(response.data["results"]) == 1
    assert Api.as_view()(factory.get("/", {"invalid": "x"})).status_code == 400
    assert Api.as_view()(factory.get("/", {"number": "invalid"})).status_code == 400
    assert isinstance(Api.as_view()(factory.get("/", {"disable_pagination": "true"})).data, list)

    class Protected(Api):
        permission_dict = {"GET": ["operators"]}

    assert Protected.as_view()(factory.get("/", {"invalid": "x"})).status_code == 403


def test_iso_week_years_are_distinct():
    now = datetime(2025, 1, 6, 12, tzinfo=dt_timezone.utc)
    Item.objects.create(name="current", event_at=now)
    Item.objects.create(name="previous", event_at=now - timedelta(days=7))
    Item.objects.create(name="older", event_at=datetime(2024, 1, 8, 12, tzinfo=dt_timezone.utc))
    with patch("handyhelpers.querysets._now", return_value=now):
        counts = count_by_week(Item.objects.all(), "event_at")
    assert counts[:2] == [1, 1] and sum(counts) == 2


def test_timezone_month_counts_and_report_queries(django_assert_num_queries):
    now = datetime(2024, 3, 1, 1, tzinfo=dt_timezone.utc)
    Item.objects.create(name="February in LA", event_at=now)
    with (
        override_settings(TIME_ZONE="America/Los_Angeles"),
        patch(
            "handyhelpers.views.report.local_now",
            return_value=now.astimezone(__import__("zoneinfo").ZoneInfo("America/Los_Angeles")),
        ),
    ):
        dataset = [{"title": "Items", "queryset": Item.objects.all(), "dt_field": "event_at"}]
        with django_assert_num_queries(1):
            labels, months, data = report.build_annual_trend_chart(dataset)
        assert months[-1].month == 2 and data[0]["data"][-1] == 1
        with django_assert_num_queries(1):
            summaries = report.build_day_week_month_year_charts(dataset)
        assert summaries[0]["day"] == 1


def test_hourly_counts_distinguish_repeated_dst_hour():
    from zoneinfo import ZoneInfo

    from handyhelpers.querysets import count_by_hour

    now = datetime(2024, 11, 3, 10, 30, tzinfo=dt_timezone.utc)
    Item.objects.create(
        name="first 1am", event_at=datetime(2024, 11, 3, 8, 30, tzinfo=dt_timezone.utc)
    )
    Item.objects.create(
        name="second 1am", event_at=datetime(2024, 11, 3, 9, 30, tzinfo=dt_timezone.utc)
    )
    with (
        override_settings(TIME_ZONE="America/Los_Angeles"),
        patch(
            "handyhelpers.querysets._now",
            return_value=now.astimezone(ZoneInfo("America/Los_Angeles")),
        ),
    ):
        counts = count_by_hour(Item.objects.all(), "event_at")
    assert counts[:3] == [0, 1, 1] and sum(counts) == 2


def test_template_fallback_without_context_processors():
    from django.template.loader import render_to_string

    html = render_to_string(
        "handyhelpers/generic/bs5/generic_about.html",
        {"base_template": "handyhelpers/handyhelpers_base_bs5.htm"},
    )
    assert "bootstrap@5.3.8" in html
    html = render_to_string("handyhelpers/generic/bs5/generic_about.html", {})
    assert "bootstrap@5.3.8" in html
