from django.db import models

from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class AnonymousUser(BaseModel, BasePermissionModel):
    name = models.CharField(max_length=60)

    class Meta:
        verbose_name_plural = "Anonymous users"

    def __str__(self):
        return self.name
