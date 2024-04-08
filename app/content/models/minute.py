from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel


class Minute(BaseModel, BasePermissionModel):
    write_access = (AdminGroup.INDEX,)
    read_access = (AdminGroup.INDEX,)

    title = models.CharField(max_length=200)
    content = models.TextField(default="", blank=True)
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="meeting_minutes",
    )

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
        return self.has_write_permission(request)

    def has_object_destroy_permission(self, request):
        return self.has_write_permission(request)

    def has_object_retrieve_permission(self, request):
        return self.has_read_permission(request)

    def __str__(self):
        return self.title
