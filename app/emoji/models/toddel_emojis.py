from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.toddel import Toddel
from app.util.models import BaseModel


class ToddelEmojis(BaseModel, BasePermissionModel):
    toddel = models.ForeignKey(Toddel, on_delete=models.CASCADE, related_name="emojis")
    emojis_allowed = models.BooleanField(default=False)

    write_access = AdminGroup.all()

    def __str__(self):
        return f"{self.toddel.title} - Emojis Allowed: {self.emojis_allowed}"
