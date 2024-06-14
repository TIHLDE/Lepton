from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel, OptionalImage


class DrinkingGame(BaseModel, OptionalImage, BasePermissionModel):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=500)

    write_access = AdminGroup.all()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]
