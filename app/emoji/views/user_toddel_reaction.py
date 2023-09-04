from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models.toddel import Toddel
from app.emoji.models.toddel_emojis import ToddelEmojis
from app.emoji.models.user_toddel_reaction import UserToddelReaction
from app.emoji.serializers.user_toddel_reaction import (
    UserToddelReactionSerializer,
)


class UserToddelReactionViewSet(BaseViewSet):

    serializer_class = UserToddelReactionSerializer
    queryset = UserToddelReaction.objects.all()
    permission_classes = [BasicViewPermission]

    def create(self, request, *args, **kwargs):
        toddel = get_object_or_404(Toddel, edition=request.data["toddel"])
        toddel_emojis = ToddelEmojis.objects.filter(toddel=toddel)
        allowed_emojis = [t.emoji.id for t in toddel_emojis]
        emoji = request.data["emoji"]

        if emoji not in allowed_emojis:
            return Response(
                {"detail": "Ulovlig emoji for denne tøddelen"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = UserToddelReactionSerializer(
            data=request.data, context={"request": request}
        )
        try:
            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError:
            return Response(
                {"detail": "Noe gikk galt"}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        toddel = get_object_or_404(Toddel, edition=request.data["toddel"])
        toddel_emojis = ToddelEmojis.objects.filter(toddel=toddel)
        allowed_emojis = [t.emoji.id for t in toddel_emojis]
        emoji = request.data["emoji"]

        if emoji not in allowed_emojis:
            return Response(
                {"detail": "Ulovlig emoji for denne tøddelen"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reaction = self.get_object()
        serializer = UserToddelReactionSerializer(
            reaction, data=request.data, context={"request": request}
        )

        try:
            if serializer.is_valid():
                super().perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                {"detail": "Du har ikke tillatelse til å oppdatere med den emojien"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UserToddelReaction.DoesNotExist as reaction_not_exist:
            capture_exception(reaction_not_exist)
            return Response(
                {"details": "Reaksjonen ble ikke funnet"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble fjernet"}, status=status.HTTP_200_OK)
