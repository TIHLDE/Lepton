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
        is_logged_in = get_user_id(request) is not None

        if not is_logged_in:
            return False

        if view.action in ["retrieve"]:
            return True

        return check_strict_group_permission(request, self.groups)

    def has_object_permission(self, request, view, obj):
        get_user_id(request)

        if isinstance(obj, EventForm) and obj.type == EventFormType.EVALUATION:
            print(obj)
            print(list(obj.event.get_queue().all()))
            return (
                obj.event.get_queue()
                .filter(user=request.user, has_attended=True)
                .exists()
            )

        return True
