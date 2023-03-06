from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models.news import News
from app.content.models.user import User
from app.emoji.models.custom_emoji import CustomEmoji
from app.util.models import BaseModel


class UserNewsReaction(BaseModel, BasePermissionModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    emoji = models.ForeignKey(CustomEmoji, on_delete=models.PROTECT)

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
