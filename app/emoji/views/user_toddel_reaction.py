from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.emoji.models.user_toddel_reaction import UserToddelReaction
from app.emoji.serializers.user_toddel_reaction import (
    UserToddelReactionSerializer,
)


class UserToddelReactionViewSet(BaseViewSet):

    serializer_class = UserToddelReactionSerializer
    queryset = UserToddelReaction.objects.all()
    permission_classes = [BasicViewPermission]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble fjernet"}, status=status.HTTP_200_OK)
