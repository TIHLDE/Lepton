from django.db import models
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission

from dry_rest_permissions.generics import DRYPermissions
from sentry_sdk import capture_exception

from app.common.enums import AdminGroup


class BasePermissionModel(models.Model):
    read_access = []
    write_access = []

    class Meta:
        abstract = True

    @classmethod
    def has_read_permission(cls, request):
        if not len(cls.read_access):
            return True
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_write_permission(cls, request):
        if not len(cls.write_access):
            return True
        return check_has_access(cls.write_access, request)

    def has_object_write_permission(self, request):
        return self.has_write_permission(request)

    def has_object_read_permission(self, request):
        return self.has_read_permission(request)


class BasicViewPermission(DRYPermissions):
    def has_permission(self, request, view):
        set_user_id(request)
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)


def check_has_access(groups_with_access, request):
    set_user_id(request)
    user = request.user

    try:
        groups = map(str, groups_with_access)
        return (
            user
            and user.memberships.filter(
                group__slug__iregex=r"(" + "|".join(groups) + ")"
            ).exists()
        )
    except Exception as e:
        capture_exception(e)
    return False


def set_user_id(request):
    token = request.META.get("HTTP_X_CSRF_TOKEN")
    request.id = None
    request.user = None

    if token is None:
        return None

    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return

    request.id = user.user_id
    request.user = user


class IsLeader(BasePermission):
    """Checks if the user is a leader on a group"""

    message = "You are not the leader of this group"

    def has_permission(self, request, view, group_slug=None):
        set_user_id(request)
        # Check if session-token is provided
        group_slug = group_slug if group_slug else view.kwargs["slug"]
        user = request.user
        memberships = user.memberships.all() if user else []
        for membership in memberships:
            if membership.group.slug == group_slug:
                return membership.is_leader()


class IsMember(BasePermission):
    """Checks if the user is a member"""

    message = "You are not a member"

    def has_permission(self, request, view):
        set_user_id(request)
        # Check if session-token is provided
        user_id = request.id

        if user_id is None:
            return False

        return True


class IsDev(BasePermission):
    """Checks if the user is in Index"""

    message = "You are not in Index"

    def has_permission(self, request, view):
        set_user_id(request)
        user_id = request.user
        if user_id is None:
            return False
        return check_has_access([AdminGroup.INDEX], request)


class IsHS(BasePermission):
    """Checks if the user is in HS or Index"""

    message = "You are not in HS"

    def has_permission(self, request, view):
        return check_has_access(AdminGroup.admin(), request)


def is_admin_user(request):
    set_user_id(request)
    """ Checks if user is in dev or HS """
    user_id = request.user

    if user_id is None:
        return False

    return check_has_access(AdminGroup.admin(), request)


def is_index_user(request):
    set_user_id(request)
    """Checks if user is in Index"""
    user_id = request.user

    if user_id is None:
        return False

    return check_has_access([AdminGroup.INDEX], request)


def is_admin_group_user(request):
    set_user_id(request)
    """Checks if user is in HS, Index, Nok, Promo, Sosialen or Kok"""
    user_id = request.user

    if user_id is None:
        return False

    return check_has_access(AdminGroup.all(), request)
