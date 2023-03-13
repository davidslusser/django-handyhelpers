"""
Description:
    Collection of helpers to assist with permissions on views

How to use:
    Add in your view as a mixin and define groups per method in permission_dict.
    Example:

        class MyView(InAnyGroup, View):
            permission_dict = {'POST': ['superusers'],
                               'GET': ['operators'] }

"""

from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import messages
from django.shortcuts import redirect


class MethodGroupPermissionBase(object):
    """ Base class for method group permissions
    This now includes a check for a settings variable, MESSAGE_ON_PERMISSION_DENY. When MESSAGE_ON_PERMISSION_DENY is
    set to True, an alert will be sent via messages and redirect will be to the HTTP_REFERER instead of redirecting to
    the LOGIN_URL. This was added to avoid a login redirect loop that can occur when certain auth packages, that deviate
    from the standard login url, are used.
    """
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission(request, *args, **kwargs):
            if getattr(settings, 'MESSAGE_ON_PERMISSION_DENY', False):
                messages.add_message(request,
                                     messages.ERROR,
                                     f'User {request.user} is not authorized to perform this operation',
                                     extra_tags='alert-danger', )
                if request.META.get('HTTP_REFERER'):
                    return redirect(request.META.get('HTTP_REFERER'))
                return redirect('/')

            elif settings.LOGIN_URL and REDIRECT_FIELD_NAME:
                return redirect_to_login(request.get_full_path(),
                                         settings.LOGIN_URL,
                                         REDIRECT_FIELD_NAME
                                         )
            else:
                raise PermissionDenied
        return super(MethodGroupPermissionBase, self).dispatch(request, *args, **kwargs)


class InAllGroups(MethodGroupPermissionBase):
    """
    Description:
        Restrict access based on request method and user group; user must be in ALL required groups

    Usage:
        add as mixin to class definition and put the following in your viewset:
            permission_dict = {'POST': ['site_operators', 'site_admins'],
                               'GET': ['site_operators'],
                              }

        to restrict POST, but allow GET for all users use the following:
            permission_dict = {'POST': ['site_admins'],
                               'GET': [],
                              }

    """
    def has_permission(self, request, *args, **kwargs):
        if not hasattr(self, 'permission_dict'):
            return False
        if request.user.is_superuser:
            return True
        permission_dict_mapping = getattr(self, 'permission_dict', {})
        permission_group_list = permission_dict_mapping.get(request.method, [])

        # if method is not provided, deny operation
        if permission_group_list is None:
            return False

        # if method is specified, but the group list is empty, allow operation
        if permission_group_list == []:
            return True

        return set(permission_group_list).issubset([i.name for i in request.user.groups.all()])


class InAnyGroup(MethodGroupPermissionBase):
    """
    Description:
        Restrict access based on request method and user group; user can be in ANY required group

    Usage:
        add as mixin to class definition and put the following in your viewset:
            permission_dict = {'POST': ['site_admins'],
                               'GET': ['site_admins', 'site_operators'],
                              }

        to restrict POST, but allow GET for all users use the following:
            permission_dict = {'POST': ['site_admins'],
                               'GET': [],
                              }
    """
    def has_permission(self, request, *args, **kwargs):
        if not hasattr(self, 'permission_dict'):
            return False
        if request.user.is_superuser:
            return True
        permission_dict_mapping = getattr(self, 'permission_dict', {})
        permission_group_list = permission_dict_mapping.get(request.method, None)

        # if method is not provided, deny operation
        if permission_group_list is None:
            return False

        # if method is specified, but the group list is empty, allow operation
        if permission_group_list == []:
            return True

        return any(group in [i.name for i in request.user.groups.all()] for group in permission_group_list)
