from django.conf import settings
from django.http import HttpResponse
from django.urls import path
from django.utils import timezone
from handyhelpers.views import action
from handyhelpers.views import htmx

if "auditlog" in settings.INSTALLED_APPS:
    from handyhelpers.views import auditlog


app_name = "handyhelpers"

urlpatterns = [
    # probes
    path("live/", lambda request: HttpResponse("live"), name="live"),
    path("ready/", lambda request: HttpResponse("ready"), name="ready"),
    path(
        "starttime/",
        lambda request: HttpResponse(f"{settings.HH_STARTTIME}"),
        name="starttime",
    ),
    path(
        "uptime/",
        lambda request: HttpResponse(f"{timezone.now() - settings.HH_STARTTIME}"),
        name="uptime",
    ),
    # action views
    path("filter_list_view", action.FilterListView.as_view(), name="filter_list_view"),
    path(
        "show_all_list_view",
        action.ShowAllListView.as_view(),
        name="show_all_list_view",
    ),
    # htmx views
    path("about", htmx.AboutProjectModalView.as_view(), name="about"),
]

if "auditlog" in settings.INSTALLED_APPS:
    urlpatterns.extend(
        [
            path(
                "get_auditlog_entries/<str:model_name>/<str:pk>/",
                auditlog.GetAuditLogEntries.as_view(),
                name="get_auditlog_entries",
            ),
            path(
                "get_auditlog_entry/<int:id>/",
                auditlog.GetAuditLogEntry.as_view(),
                name="get_auditlog_entry",
            ),
        ]
    )
