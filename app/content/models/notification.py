from django.db import models

from .user import User


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user}"

