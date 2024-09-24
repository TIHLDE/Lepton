from django.db import models

from app.codex.enums import CodexGroups
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.enums import MinuteTagEnum
from app.content.models.user import User
from app.group.models import Group
from app.util.models import BaseModel


class Minute(BaseModel, BasePermissionModel):
    write_access = CodexGroups.all()
    read_access = CodexGroups.all()

    title = models.CharField(max_length=200)
    content = models.TextField(default="", blank=True)
    tag = models.CharField(
        max_length=50, choices=MinuteTagEnum.choices, default=MinuteTagEnum.MINUTE
    )
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="meeting_minutes",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        default=CodexGroups.INDEX,
        choices=CodexGroups.choices,
        on_delete=models.SET_NULL,
        related_name="meeting_minutes",
    )

    @classmethod
    def has_create_permission(cls, request):
        data = request.data
        if "group" in data:
            return check_has_access([data["group"]], request)
        return False

    @classmethod
    def has_update_permission(cls, request):
        return cls.has_write_permission(request)

    @classmethod
    def has_destroy_permission(cls, request):
        return cls.has_write_permission(request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return cls.has_read_permission(request)

    def has_object_read_permission(self, request):
        return self.has_read_permission(request)

    def has_object_update_permission(self, request):
        data = request.data
        if "group" in data:
            return check_has_access([data["group"]], request)
        return False

    def has_object_destroy_permission(self, request):
        return check_has_access([self.group.slug], request)

    def has_object_retrieve_permission(self, request):
        return self.has_read_permission(request)

    def __str__(self):
        return self.title
