import uuid

from django.db import models

from app.common.permissions import BasePermissionModel
from app.group.models.group import Group
from app.util.models import BaseModel


class Law(BaseModel, BasePermissionModel):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="laws")
    description = models.TextField(default="", blank=True)
    paragraph = models.CharField(default="", blank=True, max_length=10)
    amount = models.IntegerField(default=1)

    class meta:
        verbose_name_plural = "Laws"

    def __str__(self):
        return f"§ {self.paragraph} - {self.description} - {self.amount} enhet"
