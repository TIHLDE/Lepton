from django.db import models

from app.common.enums import Groups
from app.common.permissions import BasePermissionModel
from app.content.models.news import News
from app.emoji.models.reaction import Reaction
from app.util.models import BaseModel


class NewsReaction(BaseModel, BasePermissionModel):
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)

    write_access = [Groups.TIHLDE]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reaction", "news"], name="unique together: reaction and news"
            )
        ]
