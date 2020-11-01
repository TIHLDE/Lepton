from rest_framework.permissions import SAFE_METHODS, BasePermission

from app.content.enums import AdminGroup
from app.content.permissions.permissions import check_strict_group_permission


class FormPermissions(BasePermission):

    def __init__(self, groups):
        self.groups = groups

    def __call__(self, *args, **kwargs):
        return self

    def has_permission(self, request, view):
        return check_strict_group_permission(
            request, self.groups
        )