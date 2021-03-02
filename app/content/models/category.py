from django.db import models

from app.common.enums import AdminGroup
from app.common.perm import BasePermissionModel
from app.util.models import BaseModel


class Category(BaseModel, BasePermissionModel):
    text = models.CharField(max_length=200, null=True)

    write_access = [AdminGroup.HS, AdminGroup.INDEX, AdminGroup.NOK, AdminGroup.PROMO]

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.text}"
