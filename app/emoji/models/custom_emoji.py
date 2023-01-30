from django.db import models
from app.common.permissions import BasePermissionModel
from app.common.enums import Groups
from app.util.models import BaseModel


class CustomEmoji(BaseModel, BasePermissionModel):
    img = models.URLField(max_length=512)

    write_access = [Groups.TIHLDE]

    def __str__(self):
        if self.short_names.exists():
            return ", ".join(name.value for name in self.short_names.all())
        else:
            return "Uten navn"
