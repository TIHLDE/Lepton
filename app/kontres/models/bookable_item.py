from django.db import models
from app.util.models import BaseModel
from app.common.permissions import BasePermissionModel
import uuid


class BookableItem(BaseModel, BasePermissionModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
