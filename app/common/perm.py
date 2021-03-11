from django.db import models
from rest_framework.authtoken.models import Token
from app.content.models.user import User
from dry_rest_permissions.generics import DRYPermissions


class BasePermissionModel(models.Model):
    read_access = []
    write_access = []

    class Meta:
        abstract = True

    @classmethod
    def has_read_permission(cls, request):
        if len(cls.read_access) == 0:
            return True
        return check_permissions(cls.read_access, request)

    @classmethod
    def has_write_permission(cls, request):
        if len(cls.write_access) == 0:
            return True
        return check_permissions(cls.write_access, request)

    def has_object_write_permission(self, request):
        if len(self.write_access) == 0:
            return True
        return check_permissions(self.write_access, request)

    def has_object_read_permission(self, request):
        if len(self.read_access) == 0:
            return True
        return check_permissions(self.read_access, request)


class BasicViewPermission(DRYPermissions):
    def has_permission(self, request, view):
        set_user_id(request)
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        set_user_id(request)
        return super().has_object_permission(request, view, obj)

def check_permissions(access, request):
    if get_user_id(request):
        return check_has_access(access=access, user=request.user)
    return check_has_access(access=access, request=request)


def get_user_from_request(request):
    token = request.META.get("HTTP_X_CSRF_TOKEN")

    if token is None:
        return False

    try:
        userToken = Token.objects.get(key=token)
    except Token.DoesNotExist:
        return False

    return User.objects.get(user_id=userToken.user_id)


def check_has_access(access, request=None, user=None):
    try:
        user = get_user_from_request(request) if user is None else user
        memberships = user.membership.all()
        for membership in memberships:
            for name in access:
                if str(membership.group_id).lower() == str(name).lower():
                    return True
        return False
    except Exception:
        return False


def get_user_id(request):
    token = request.META.get("HTTP_X_CSRF_TOKEN")

    if token is None:
        return None

    try:
        userToken = Token.objects.get(key=token)
    except Token.DoesNotExist:
        return None

    return userToken.user_id

def set_user_id(request):
    token = request.META.get("HTTP_X_CSRF_TOKEN")
    request.id = None
    request.user = None

    if token is None:
        return None

    try:
        userToken = Token.objects.get(key=token)
    except Token.DoesNotExist:
        return None

    request.id = userToken.user_id
    request.user = User.objects.get(user_id = userToken.user_id)

