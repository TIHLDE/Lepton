from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.blitzed.models.drinking_game import DrinkingGame
from app.blitzed.serializers.drinking_game import DrinkingGameSerializer
from app.common.permissions import BasicViewPermission


class DrinkingGameViewSet(ModelViewSet):
    queryset = DrinkingGame.objects.all().order_by("-created_at")
    serializer_class = DrinkingGameSerializer
    permission_classes = [BasicViewPermission]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "The drinking game was deleted"}, status=status.HTTP_200_OK
        )
