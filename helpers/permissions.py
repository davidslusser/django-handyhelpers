from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME


class MethodGroupPermissions(object):
    """
    Description:
        Restrict access based on request method and user group

    Usage:
        permission_dict must be in the view example:
        class MyViewClass(MethodGroupPermissions, DetailView)
            permission_dict = {'POST': ['site_admins'],
                               'GET': ['site_operators']
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
