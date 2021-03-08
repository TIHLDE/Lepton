from django.db import models

from app.content.models.user import User
from app.util.models import BaseModel


class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user}"
