from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models.news import News
from app.content.models.user import User
from app.util.models import BaseModel


class UserNewsReactionUnicode(BaseModel, BasePermissionModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    news = models.ForeignKey(
        News, on_delete=models.CASCADE, related_name="user_reactions"
    )
    emoji = models.CharField(max_length=60)

    write_access = [Groups.TIHLDE]
    read_access = [Groups.TIHLDE]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "news"], name="unique together: user and news"
            )
        ]

    def __str__(self):
        return f"{self.news.title} - {self.emoji}"
