from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from app.util.models import BaseModel
from app.common.permissions import BasePermissionModel
from app.common.enums import Groups
from app.content.models.user import User


class Comment(BaseModel, BasePermissionModel):
    write_access = (Groups.TIHLDE, )
    read_access = (Groups.TIHLDE, )

    body = models.TextField()

    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="comments"
    )

    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="children",
        verbose_name="parent"
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        ordering = ("-created_at",)
    
    def __str__(self):
        return f"Comment by: {self.author.first_name} {self.author.last_name} - created: {self.created_at}"