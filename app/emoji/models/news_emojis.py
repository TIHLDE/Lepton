from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.news import News
from app.emoji.models.custom_emoji import CustomEmoji
from app.util.models import BaseModel


class NewsEmojis(BaseModel, BasePermissionModel):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="emojis")
    emoji = models.ForeignKey(CustomEmoji, on_delete=models.PROTECT)

    write_access = AdminGroup.all()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["news", "emoji"], name="unique together: news and emoji"
            )
        ]

    def __str__(self):
        return f"{self.news.title} - {self.emoji}"
