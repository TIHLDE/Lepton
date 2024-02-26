from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from app.common.enums import Groups
from app.common.permissions import (
    BasePermissionModel,
    check_has_access,
    is_admin_user,
)
from app.content.models import User
from app.util.models import BaseModel


class Comment(BaseModel, BasePermissionModel):
    write_access = (Groups.TIHLDE,)
    read_access = (Groups.TIHLDE,)

    body = models.TextField()
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="parent",
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, default=None
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        if self.author:
            return f"Comment by {self.author.first_name} {self.author.last_name} - Created at {self.created_at}"
        else:
            return f"Comment by deleted user - Created at {self.created_at}"

    """def has_object_write_permission(self, request):
        if request.method == "DELETE":
            return(self.has_write_permission(request) and self.author == request.user) or is_admin_user(request)
        return self.has_write_permission(request) and self.author == request.user"""

    @classmethod
    def has_update_permission(cls, request):
        return check_has_access(cls.write_access, request)

    def has_object_update_permission(self, request):
        return self.author == request.user

    @classmethod
    def has_destroy_permission(cls, request):
        return check_has_access(cls.write_access, request)

    def has_object_destroy_permission(self, request):
        return self.author == request.user or is_admin_user(request)

    @classmethod
    def has_retrieve_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_list_permission(cls, request):
        return check_has_access(cls.read_access, request)

    @classmethod
    def has_create_permission(cls, request):
        return check_has_access(cls.write_access, request)
