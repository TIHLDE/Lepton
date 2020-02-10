from django.db import models

from .user import User

class Notification(models.Model):
    """ Model for notifications """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    unread = models.BooleanField(default=True)
