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
