from rest_framework.permissions import BasePermission

from app.common.permissions import check_strict_group_permission, get_user_id
from app.forms.enums import EventFormType
from app.forms.models.forms import EventForm


class FormPermissions(BasePermission):
    def __init__(self, groups):
        self.groups = groups

    def __call__(self, *args, **kwargs):
        return self

    def has_permission(self, request, view):
        get_user_id(request)

        if not request.user.is_authenticated:
            return False

        if view.action in ["retrieve"]:
            return True

        return check_strict_group_permission(request, self.groups)

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, EventForm) and obj.type == EventFormType.EVALUATION:
            return (
                obj.event.get_queue()
                .filter(user=request.user, has_attended=True)
                .exists()
            )

        return True


class SubmissionPermissions(BasePermission):
    def __init__(self, groups):
        self.groups = groups

    def __call__(self, *args, **kwargs):
        return self

    def has_permission(self, request, view):
        get_user_id(request)

        if not request.user.is_authenticated:
            return False

        if view.action in ["create"]:
            return True

        return check_strict_group_permission(request, self.groups)
