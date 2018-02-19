from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from rest_framework.permissions import BasePermission, SAFE_METHODS


class MethodGroupPermissions(object):
    """ Restrict access based on request method and user group

        permission_dict must be in the view example:
            permission_dict = {'POST': ['my_restricted_group'],
                               'GET': ['my_unrestricted_group']
                              }
    """
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request, *args, **kwargs):
            if settings.LOGIN_URL and REDIRECT_FIELD_NAME:
                return redirect_to_login(request.get_full_path(),
                                         settings.LOGIN_URL,
                                         REDIRECT_FIELD_NAME
                                         )
            else:
                raise PermissionDenied
        return super(MethodGroupPermissions, self).dispatch(request, *args, **kwargs)

    def has_permission(self, request, *args, **kwargs):
        if not hasattr(self, 'permission_dict'):
            return False
        permission_dict_mapping = getattr(self, 'permission_dict', {})
        permission_dict = permission_dict_mapping.get(request.method, [])
        return set(permission_dict).issubset([i.name for i in request.user.groups.all()])


class IsAdminOrReadOnly(BasePermission):
    """ The request is authenticated as an admin, or is a read-only request. """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class IsInGroup(BasePermission):
    """ Restrict access based on request method and user group """
    def has_permission(self, request, view):
        required_groups_mapping = getattr(view, 'required_groups', {})
        required_groups = required_groups_mapping.get(request.method, [])
        if required_groups is None:
            return False
        return set(required_groups).issubset([i.name for i in request.user.groups.all()])
