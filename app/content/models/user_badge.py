from django.db import models

from app.content.models import Badge, User
from app.util.models import BaseModel


class UserBadge(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_badges")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "User badge"
        verbose_name_plural = "User badges"

    def __str__(self):
        return f"{self.badge.title} - {self.user.user_id}"
