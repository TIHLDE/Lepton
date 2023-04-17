from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.toddel import Toddel
from app.emoji.models.custom_emoji import CustomEmoji
from app.util.models import BaseModel


class ToddelEmojis(BaseModel, BasePermissionModel):
    toddel = models.ForeignKey(Toddel, on_delete=models.CASCADE, related_name="emojis")
    emoji = models.ForeignKey(CustomEmoji, on_delete=models.PROTECT)

    write_access = AdminGroup.all()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["toddel", "emoji"], name="unique together: toddel and emoji"
            )
        ]

    def __str__(self):
        return f"{self.toddel.title} - {self.emoji}"
