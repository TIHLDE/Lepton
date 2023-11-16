from django.db import models


class ContentTypes(models.TextChoices):
    NEWS = ("news",)
    EVENT = ("event",)
