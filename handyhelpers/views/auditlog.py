"""Permission-protected optional audit-log endpoints."""

from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from handyhelpers.utils import optional_import

from .ajax import AjaxGetView

LogEntry = optional_import("auditlog.models", "auditlog").LogEntry


def check_model_permission(user, model):
    if model is None or not user.has_perm(f"{model._meta.app_label}.view_{model._meta.model_name}"):
        raise PermissionDenied


class GetAuditLogEntries(LoginRequiredMixin, AjaxGetView):
    template_name = "handyhelpers/ajax/get_auditlog_entries.htm"

    def get(self, request, *args, **kwargs):
        try:
            model = apps.get_model(kwargs["app_label"], kwargs["model_name"])
        except LookupError as error:
            raise Http404 from error
        check_model_permission(request.user, model)
        content_type = ContentType.objects.get_for_model(model, for_concrete_model=False)
        self.data = (
            LogEntry.objects.filter(content_type=content_type, object_pk=kwargs["pk"])
            .select_related("actor")
            .order_by("-timestamp")
        )
        return super().get(request, *args, **kwargs)


class GetAuditLogEntry(LoginRequiredMixin, AjaxGetView):
    template_name = "handyhelpers/ajax/get_auditlog_entry.htm"

    def get(self, request, *args, **kwargs):
        self.data = get_object_or_404(
            LogEntry.objects.select_related("content_type", "actor"), pk=kwargs["id"]
        )
        check_model_permission(request.user, self.data.content_type.model_class())
        return super().get(request, *args, **kwargs)
