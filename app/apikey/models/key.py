import uuid

from django.db import models

from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class ApiKey(BaseModel, BasePermissionModel):
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"API Key: {self.key} - {self.title}"
