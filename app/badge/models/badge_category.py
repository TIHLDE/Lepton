import uuid

from django.db import models

from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel, OptionalImage


class BadgeCategory(BaseModel, OptionalImage, BasePermissionModel):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, serialize=False,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(default="", blank=True)

    class Meta:
        verbose_name_plural = "Badge Categories"

    def __str__(self):
        return self.name
