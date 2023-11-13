from django.db import models
from django.utils.safestring import mark_safe

from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class BeerpongTournament(BaseModel, BasePermissionModel):
    name = models.CharField(max_length=60)

    class Meta:
        verbose_name_plural = "Pong tournaments"

    def __str__(self):
        return mark_safe(self.name)
