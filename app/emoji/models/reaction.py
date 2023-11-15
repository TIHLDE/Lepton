from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel


class Reaction(BaseModel, BasePermissionModel):
    write_access = (Groups.TIHLDE,)
    read_access = (Groups.TIHLDE,)

    reaction_id = models.AutoField(primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    emoji = models.CharField(max_length=60)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ("user", "object_id", "content_type")
        verbose_name = "Reaction"
        verbose_name_plural = "Reactions"

    def __str__(self):
        return f"{self.user.first_name} - {self.emoji}"

    def has_object_write_permission(self, request):
        return self.user == request.user and super().has_object_write_permission(
            request
        )
