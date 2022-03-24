from django.db import models

from app.common.enums import AdminGroup, Groups
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel
from app.util.utils import datetime_format


class Toddel(BaseModel, BasePermissionModel):
    edition = models.IntegerField(primary_key=True, unique=True)
    title = models.CharField(max_length=200)
    image = models.URLField(max_length=600)
    pdf = models.URLField(max_length=600)
    published_at = models.DateField()

    write_access = (*AdminGroup.admin(), Groups.REDAKSJONEN)

    class Meta:
        verbose_name = "Töddel"
        verbose_name_plural = "Töddel"
        ordering = ("-edition",)

    def __str__(self):
        return f"Edition {self.edition} - {self.title} ({datetime_format(self.published_at)})"
