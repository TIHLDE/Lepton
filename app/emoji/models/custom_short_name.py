from django.core.validators import RegexValidator
from django.db import models

from app.emoji.models.custom_emoji import CustomEmoji


class CustomShortName(models.Model):
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
    emoji = models.ForeignKey(
        CustomEmoji,
        related_name="short_names",
        on_delete=models.CASCADE,
        auto_created=True,
    )

    def __str__(self):
        return self.value
