"""
Permissions classes used with DRF APIs
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """ The request is authenticated as an admin, or is a read-only request. """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class IsInAllGroups(BasePermission):
    """ 
    Description:
        Restrict access based on request method and user group; user must be in ALL required groups 
    
    Usage:
        put the following in your viewset:
            permission_classes = (IsInAllGroups,)
            required_groups = {'POST': ['site_admins'],
                               'PATCH': ['site_admins'],
                               'PUT': ['site_admins'],
                               'DELETE': ['site_admins', 'site_managers'],
                              }
    """
    def has_permission(self, request, view):
        required_groups_mapping = getattr(view, 'required_groups', {})
        required_groups = required_groups_mapping.get(request.method, [])
        if required_groups is None:
            return False
        return set(required_groups).issubset([i.name for i in request.user.groups.all()])


class IsInAnyGroup(BasePermission):
    """ 
    Description:
        Restrict access based on request method and user group; user can be in ANY required group 
    
    Usage:
        put the following in your viewset:
            permission_classes = (IsInAnyGroup,)
            required_groups = {'POST': ['site_admins'],
                               'PATCH': ['site_admins'],
                               'PUT': ['site_admins'],
                               'DELETE': ['site_admins', 'superusers'],
                              }
    """
    def has_permission(self, request, view):
        required_groups_mapping = getattr(view, 'required_groups', {})
        required_groups = required_groups_mapping.get(request.method, [])
        if required_groups is None:
            return False
        return any(group in [i.name for i in request.user.groups.all()] for group in required_groups)


class InAllGroups(BasePermission):
    """
    Description:
        Restrict access based on request method and user group; user must be in ALL required groups

    Usage:
        put the following in your viewset:
            permission_classes = (InAllGroups,)
            permission_dict = {'POST': ['site_admins'],
                               'PATCH': ['site_admins'],
                               'PUT': ['site_admins'],
                               'DELETE': ['site_admins', 'site_managers'],
                              }
    """

    def has_permission(self, request, view):
        if not hasattr(view, 'permission_dict'):
            return False
        if request.user.is_superuser:
            return True
        permission_dict_mapping = getattr(view, 'permission_dict', {})
        permission_group_list = permission_dict_mapping.get(request.method, [])

        # if method is not provided, deny operation
        if permission_group_list is None:
            return False

        # if method is specified, but the group list is empty, allow operation
        if permission_group_list == []:
            return True

        return set(permission_group_list).issubset([i.name for i in request.user.groups.all()])


class InAnyGroup(BasePermission):
    """
    Description:
        Restrict access based on request method and user group; user can be in ANY required group

    Usage:
        put the following in your viewset:
            permission_classes = (InAnyGroup,)
            permission_dict = {'POST': ['site_admins'],
                               'PATCH': ['site_admins'],
                               'PUT': ['site_admins'],
                               'DELETE': ['site_admins', 'superusers'],
                              }
    """

    def has_permission(self, request, view):
        if not hasattr(view, 'permission_dict'):
            return False
        if request.user.is_superuser:
            return True

        permission_dict_mapping = getattr(view, 'permission_dict', {})
        permission_group_list = permission_dict_mapping.get(request.method, None)

        # if method is not provided, deny operation
        if permission_group_list is None:
            return False

        # if method is specified, but the group list is empty, allow operation
        if permission_group_list == []:
            return True

        return any(group in [i.name for i in request.user.groups.all()] for group in permission_group_list)
