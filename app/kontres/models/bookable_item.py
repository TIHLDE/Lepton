import uuid

from django.db import models

from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class BookableItem(BaseModel, BasePermissionModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
