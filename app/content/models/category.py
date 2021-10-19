from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class Category(BaseModel, BasePermissionModel):
    write_access = AdminGroup.all()
    text = models.CharField(max_length=200, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.text}"
