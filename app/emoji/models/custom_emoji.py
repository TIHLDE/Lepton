from django.db import models


class CustomEmoji(models.Model):
    img = models.URLField(max_length=512)

    @classmethod
    def has_read_permission(cls, request):
        return True

    @classmethod
    def has_write_permission(cls, request):
        return True
