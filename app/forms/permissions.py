from rest_framework.permissions import BasePermission

from app.common.permissions import check_strict_group_permission, get_user_id
from app.forms.enums import FormType


class FormPermissions(BasePermission):
    def __init__(self, groups):
        self.groups = groups

    def __call__(self, *args, **kwargs):
        return self

    def has_object_permission(self, request, view, obj):
        get_user_id(request)

        #  If user is admin.
        if check_strict_group_permission(request, self.groups):
            return True

        #  If the form type is evaluation, return True if the user has attended the event.
        if obj.type == FormType.EVALUATION:
            return request.user in obj.event.registered_users_list

        #  If not, all users should have access.
        return True
