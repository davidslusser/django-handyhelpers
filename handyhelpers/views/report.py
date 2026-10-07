"""Calendar-based reporting with database aggregation and serialized chart data."""

from datetime import timedelta
from itertools import cycle, islice

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from handyhelpers.mixins.view_mixins import HtmxViewMixin
from handyhelpers.utils import base_template_name, update_query

PERIODS = ("day", "week", "month", "year")


def get_color_list():
    return [
        "primary",
        "success",
        "secondary",
        "info",
        "warning",
        "danger",
        "dark",
        "light",
        "blue",
        "green",
        "red",
        "orange",
        "yellow",
        "purple",
        "teal",
        "cyan",
        "indigo",
        "pink",
        "white",
        "gray",
        "gray-dark",
    ]


def get_colors(count):
    return list(islice(cycle(get_color_list()), count))


def local_now():
    now = timezone.now()
    return timezone.localtime(now) if timezone.is_aware(now) else now


def get_annual_timestamps(start=None, end=None, reverse=False):
    """Month boundaries, including the current month (12 months by default)."""
    end = end or local_now()
    last = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first = (
        start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start
        else last - relativedelta(months=11)
    )
    months = []
    while first <= last:
        months.append(first)
        first += relativedelta(months=1)
    return list(reversed(months)) if reverse else months


def get_timestamps(now=None):
    now = now or local_now()
    return (
        now - timedelta(days=1),
        now - timedelta(days=7),
        now - relativedelta(months=1),
        now - relativedelta(years=1),
    )


def get_dated_data(queryset, ts_lookup):
    return tuple(queryset.filter(**{ts_lookup: boundary}) for boundary in get_timestamps())


def _annual_data(dataset_list, cumulative=False):
    now = local_now()
    months = get_annual_timestamps(end=now)
    datasets = []
    for dataset, color in zip(dataset_list, get_colors(len(dataset_list)), strict=True):
        field = dataset["dt_field"]
        queryset = dataset["queryset"].all()
        rows = (
            queryset.filter(**{field + "__gte": months[0], field + "__lte": now})
            .annotate(month=TruncMonth(field))
            .order_by()
            .values("month")
            .annotate(count=Count("pk"))
        )
        counts = {(row["month"].year, row["month"].month): row["count"] for row in rows}
        total = queryset.filter(**{field + "__lt": months[0]}).count() if cumulative else 0
        values = []
        urls = []
        for month in months:
            count = counts.get((month.year, month.month), 0)
            total = total + count if cumulative else count
            values.append(total)
            end = min(month + relativedelta(months=1), now)
            filters = {field + "__lt": end.isoformat(), "page_description": month.strftime("%B %Y")}
            if not cumulative:
                filters[field + "__gte"] = month.isoformat()
            urls.append(update_query(dataset.get("list_view") or "/", filters))
        datasets.append(
            {
                **{key: value for key, value in dataset.items() if key != "queryset"},
                "data": values,
                "annual": values,
                "color": color,
                "urls": urls,
            }
        )
    return [month.strftime("%B %Y") for month in months], months, datasets


def build_annual_progress_chart(dataset_list):
    return _annual_data(dataset_list, cumulative=True)


def build_annual_trend_chart(dataset_list):
    return _annual_data(dataset_list)


def build_day_week_month_year_charts(dataset_list):
    now = local_now()
    boundaries = get_timestamps(now)
    results = []
    for dataset, color in zip(dataset_list, get_colors(len(dataset_list)), strict=True):
        field = dataset["dt_field"]
        counts = dataset["queryset"].aggregate(
            total=Count("pk"),
            **{
                period: Count("pk", filter=Q(**{field + "__gte": boundary, field + "__lte": now}))
                for period, boundary in zip(PERIODS, boundaries, strict=True)
            },
        )
        data = {
            **{key: value for key, value in dataset.items() if key != "queryset"},
            **counts,
            "color": color,
        }
        for period, boundary in zip(PERIODS, boundaries, strict=True):
            data[period + "_date"] = boundary
            data[period + "_count"] = counts[period]
            data[period + "_url"] = update_query(
                dataset.get("list_view") or "/",
                {
                    field + "__gte": boundary.isoformat(),
                    field + "__lte": now.isoformat(),
                    "page_description": "added in past " + period,
                },
            )
        data["url"] = dataset.get("list_view")
        results.append(data)
    return results


def _line_chart(labels, datasets):
    return {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": data["title"],
                    "data": data["data"],
                    "borderColor": data["color"],
                    "backgroundColor": data["color"],
                    "fill": False,
                    "tension": 0.4,
                    "urls": data["urls"],
                }
                for data in datasets
            ],
        },
        "options": {"responsive": True, "plugins": {"legend": {"display": True}}},
    }


class AnnualStatView(HtmxViewMixin, View):
    base_template = None
    title = "Annual Statistics Report"
    sub_title = None
    template_name = "handyhelpers/report/annual_stats.html"
    htmx_template_name = "handyhelpers/report/annual_stats_content.htm"
    dataset_list = ()

    def get_context_data(self):
        return {
            "base_template": base_template_name(self.base_template),
            "title": self.title,
            "sub_title": self.sub_title,
            "dataset_list": build_day_week_month_year_charts(self.dataset_list),
        }

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.htmx_template_name if self.is_htmx() else self.template_name,
            self.get_context_data(),
        )


class AnnualTrendView(AnnualStatView):
    title = "Annual Trend Report"
    sub_title = "data added over the past year"
    template_name = "handyhelpers/report/chartjs/annual_trends.html"
    htmx_template_name = "handyhelpers/report/chartjs/annual_trends_content.htm"
    chart_display_title = True
    chart_display_legend = False

    def get_context_data(self):
        context = super().get_context_data()
        labels, months, datasets = build_annual_trend_chart(self.dataset_list)
        context.update(
            month_labels=labels,
            month_timestamps=months,
            annual_trend_dataset_list=datasets,
            annual_trend_chart=_line_chart(labels, datasets),
        )
        for period in PERIODS:
            context[period + "_chart"] = {
                "type": "bar",
                "data": {
                    "labels": [data["title"] for data in context["dataset_list"]],
                    "datasets": [
                        {
                            "data": [data[period] for data in context["dataset_list"]],
                            "backgroundColor": [data["color"] for data in context["dataset_list"]],
                            "urls": [data[period + "_url"] for data in context["dataset_list"]],
                        }
                    ],
                },
                "options": {
                    "plugins": {
                        "title": {"display": self.chart_display_title, "text": period.title()},
                        "legend": {"display": self.chart_display_legend},
                    },
                    "scales": {"y": {"beginAtZero": True}},
                },
            }
        return context


class AnnualProgressView(AnnualStatView):
    title = "Annual Progress Report"
    sub_title = "cumulative data added over the past year"
    template_name = "handyhelpers/report/chartjs/annual_progress.html"
    htmx_template_name = "handyhelpers/report/chartjs/annual_progress_content.htm"

    def get_context_data(self):
        labels, months, datasets = build_annual_progress_chart(self.dataset_list)
        return {
            "base_template": base_template_name(self.base_template),
            "title": self.title,
            "sub_title": self.sub_title,
            "month_labels": labels,
            "month_timestamps": months,
            "annual_progress_dataset_list": datasets,
            "annual_progress_chart": _line_chart(labels, datasets),
        }
