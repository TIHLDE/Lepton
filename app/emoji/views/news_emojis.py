from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.emoji.models.news_emojis import NewsEmojis
from app.emoji.serializers.news_emojis import NewsEmojisSerializer


class NewsEmojisViewSet(BaseViewSet):

    serializer_class = NewsEmojisSerializer
    queryset = NewsEmojis.objects.all()
    permission_classes = [BasicViewPermission]

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

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)
