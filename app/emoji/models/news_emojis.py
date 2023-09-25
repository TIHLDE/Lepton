from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.news import News
from app.util.models import BaseModel


class NewsEmojis(BaseModel, BasePermissionModel):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="emojis")
    emojis_allowed = models.BooleanField(default=False)

    write_access = AdminGroup.all()

    def __str__(self):
        return f"{self.news.title} - Emojis Allowed: {self.emojis_allowed}"
