from django.db import models
from app.util.models import BaseModel
from app.content.models.news import News
from app.content.models.user import User
from app.emoji.models.custom_emoji import CustomEmoji
from app.common.permissions import BasePermissionModel
from app.common.enums import Groups

class UserNewsReaction(BaseModel, BasePermissionModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    news = models.ForeignKey(News, on_delete=models.CASCADE, primary_key=True)
    emoji = models.ForeignKey(CustomEmoji)

    write_access = [Groups.TIHLDE]

    def __str__(self):
        return f"{self.news.title} - {self.emoji}"


