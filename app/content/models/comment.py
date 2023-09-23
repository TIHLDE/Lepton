from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models.event import Event
from app.content.models.user import User
from app.util.models import BaseModel


class Comment(BaseModel, BasePermissionModel):
    write_access = (Groups.TIHLDE,)
    read_access = (Groups.TIHLDE,)

    body = models.TextField()
    user = models.ForeignKey(
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
        on_delete=models.SET_NULL,
        related_name="children",
        verbose_name="parent",
    )

    event = models.ForeignKey(
        Event,
        blank=True,
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="comments",
    )

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Comment by {self.user.first_name} {self.user.last_name} - Created at {self.created_at}"
