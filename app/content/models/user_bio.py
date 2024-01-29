from django.db import models

from app.content.models.user import User


class UserBio(models.Model):

    description = models.CharField(max_length=50)

    gitHub_link = models.URLField(max_length=300, blank=True, null=True)

    linkedIn_link = models.URLField(max_length=300, blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bio")
