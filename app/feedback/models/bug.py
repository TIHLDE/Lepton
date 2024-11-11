from django.db import models

from app.feedback.models.feedback import Feedback


class Bug(Feedback):
    url = models.URLField(max_length=200, blank=True, null=True)
    browser = models.CharField(max_length=200, default="")
    platform = models.CharField(max_length=200, default="")
