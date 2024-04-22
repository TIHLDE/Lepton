from django.db import models

from app.blitzed.models.drinking_game import DrinkingGame
from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel


class Question(BaseModel, BasePermissionModel):
    text = models.TextField(blank=True, null=True, default=None)
    drinking_game = models.ForeignKey(
        DrinkingGame, on_delete=models.CASCADE, related_name="questions"
    )

    write_access = AdminGroup.all()

    def __str__(self):
        return self.text
