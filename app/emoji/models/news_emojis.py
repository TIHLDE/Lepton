from django.db import models

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel, check_has_access
from app.content.models.news import News
from app.emoji.models.custom_emoji import CustomEmoji
from app.util.models import BaseModel


class NewsEmojis(BaseModel, BasePermissionModel):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    emoji = models.ForeignKey(CustomEmoji, on_delete=models.PROTECT)

    write_access = (*AdminGroup.admin(), AdminGroup.PROMO)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["news", "emoji"], name="unique together: news and emoji"
            )
        ]

    @classmethod
    def has_write_permission(cls, request):
        if request.user is None:
            return False
        return (
            (
                check_has_access(cls.write_access, request)
                or cls.check_request_user_has_access_through_organizer(
                    cls, request.user, request.data["organizer"]
                )
            )
            if request.data.get("organizer", None)
            else request.user.memberships_with_events_access.exists()
        )

    @classmethod
    def has_write_all_permission(cls, request):
        if request.user is None:
            return False
        return check_has_access(cls.write_access, request)

    def __str__(self):
        return f"{self.news.title} - {self.emoji}"
