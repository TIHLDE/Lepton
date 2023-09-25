from django.db import models
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.enums import AdminGroup
from app.common.permissions import BasePermissionModel
from app.content.models.news import News
from app.util.models import BaseModel


class NewsEmojis(BaseModel, BasePermissionModel):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="emojis")
    emojis_allowed = models.BooleanField(default=False)

    write_access = AdminGroup.all()

    @action(detail=False, methods=["get"])
    def get_emojis_allowed_status(self, request, news_id):
        try:
            news_emojis = NewsEmojis.objects.get(news__id=news_id)
            emojis_allowed = news_emojis.emojis_allowed

            return Response(
                {"emojis_allowed": emojis_allowed}, status=status.HTTP_200_OK
            )
        except NewsEmojis.DoesNotExist:
            return Response(
                {"detail": "Fant ikke koblingen for nyheten"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def __str__(self):
        return f"{self.news.title} - Emojis Allowed: {self.emojis_allowed}"
