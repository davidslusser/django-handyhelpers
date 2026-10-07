"""Method/group permissions for the optional Django REST framework integration."""

from handyhelpers.permissions import group_permission
from handyhelpers.utils import optional_import

permissions = optional_import("rest_framework.permissions", "api")


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or bool(
            request.user and request.user.is_staff
        )


class InAllGroups(permissions.BasePermission):
    all_groups = True

    def has_permission(self, request, view):
        return group_permission(
            request.user,
            request.method,
            getattr(view, "permission_dict", None) or {},
            self.all_groups,
        )


class InAnyGroup(InAllGroups):
    all_groups = False
