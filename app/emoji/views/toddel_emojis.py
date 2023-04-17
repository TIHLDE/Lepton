from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.emoji.models.toddel_emojis import ToddelEmojis
from app.emoji.serializers.toddel_emojis import ToddelEmojisSerializer


class ToddelEmojisViewSet(BaseViewSet):

    serializer_class = ToddelEmojisSerializer
    queryset = ToddelEmojis.objects.all()
    permission_classes = [BasicViewPermission]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)
