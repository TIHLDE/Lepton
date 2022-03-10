from django.db import models
from django.core.validators import RegexValidator

from app.emoji.models import CustomEmoji
from app.util.models import BaseModel


class CustomShortName(BaseModel):
    value = models.CharField(
        primary_key=True,
        max_length=32,
        validators=(
            RegexValidator(
                regex="[a-z_]+",
                message="Det er bare tillatt med små bokstaver og understrek.",
            ),
        ),
    )
    emoji = models.ForeignKey(CustomEmoji, on_delete=models.CASCADE)
