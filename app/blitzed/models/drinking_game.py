from django.db import models

from app.blitzed.models.question import Question
from app.common.permissions import BasePermissionModel
from app.util.models import BaseModel, OptionalImage
from app.common.enums import AdminGroup


class DrinkingGame(BaseModel, OptionalImage, BasePermissionModel):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    questions = models.ManyToManyField(
        Question, blank=True, related_name="drinking_games"
    )

    write_access = AdminGroup.all()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]