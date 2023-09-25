import uuid

from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models.user import User
from app.util.models import BaseModel


class Reaction(BaseModel, BasePermissionModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    emoji = models.CharField(max_length=60)

    write_access = [Groups.TIHLDE]
    read_access = [Groups.TIHLDE]

    class Meta:
        verbose_name = "Reaction"
        verbose_name_plural = "Reactions"

    def __str__(self):
        return f"{self.user.first_name} - {self.emoji}"
