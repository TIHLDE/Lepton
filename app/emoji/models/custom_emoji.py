from django.db import models

from app.util.models import BaseModel


class CustomEmoji(BaseModel):
    img = models.URLField(max_length=512)

    @classmethod
    def has_read_permission(cls, request):
        return True

    @classmethod
    def has_write_permission(cls, request):
        return True
