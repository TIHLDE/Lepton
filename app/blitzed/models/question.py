from django.db import models

from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class Question(BaseModel, BasePermissionModel):
    text = models.TextField(blank=True, null=True, default=None)

    def __str__(self):
        return self.text
