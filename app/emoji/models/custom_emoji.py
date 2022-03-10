from django.db import models

from app.util.models import BaseModel


class CustomEmoji(BaseModel):
    img = models.URLField(max_length=512)
