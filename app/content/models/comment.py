from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from app.common.permissions import is_admin_user


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

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=None)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Comment by {self.author.first_name} {self.author.last_name} - Created at {self.created_at}"

    def has_object_write_permission(self, request):
        if request.method == "DELETE":
            return (self.has_write_permission(request) and self.author == request.user) or is_admin_user(request)
        return self.has_write_permission(request) and self.author == request.user