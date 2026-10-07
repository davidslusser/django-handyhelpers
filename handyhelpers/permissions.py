"""Method/group permission mixins for Django views."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from handyhelpers.utils import safe_return_url


def group_permission(user, method, permission_dict, all_groups):
    groups = permission_dict.get(method)
    if groups is None:
        return False
    if groups == []:
        return True
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    names = set(user.groups.values_list("name", flat=True))
    return set(groups).issubset(names) if all_groups else bool(names.intersection(groups))


class MethodGroupPermissionBase:
    permission_dict = None
    all_groups = True

    def has_permission(self, request, *args, **kwargs):
        return group_permission(
            getattr(request, "user", None),
            request.method,
            self.permission_dict or {},
            self.all_groups,
        )

    def dispatch(self, request, *args, **kwargs):
        if self.has_permission(request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if getattr(settings, "MESSAGE_ON_PERMISSION_DENY", False):
            messages.error(request, "You are not authorized to perform this operation.")
            return redirect(safe_return_url(request))
        raise PermissionDenied


class InAllGroups(MethodGroupPermissionBase):
    """Require every group configured for the request method."""


class InAnyGroup(MethodGroupPermissionBase):
    """Require at least one group configured for the request method."""

    all_groups = False
