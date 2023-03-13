from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.emoji.models.news_emojis import NewsEmojis
from app.emoji.serializers.news_emojis import NewsEmojisSerializer


class NewsEmojisViewSet(BaseViewSet):

    serializer_class = NewsEmojisSerializer
    queryset = NewsEmojis.objects.all()
    permission_classes = [BasicViewPermission]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)
