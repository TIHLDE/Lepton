from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models.news import News
from app.emoji.serializers.reaction import ReactionSerializer


class ReactionViewSet(BaseViewSet):

    serializer_class = ReactionSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def create(self, request, *args, **kwargs):
        news = get_object_or_404(News, id=request.data["news"])
        if not news.emojis_allowed:
            return Response(
                {"detail": "Reaksjoner er ikke tillatt her."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ReactionSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            super().perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": "Kunne ikke reagere fordi noe gikk galt"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        news = get_object_or_404(News, id=request.data["news"])
        if not news.emojis_allowed:
            return Response(
                {"detail": "Reaksjoner er ikke tillatt her."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reaction = self.get_object()
        serializer = ReactionSerializer(
            reaction, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            super().perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": "Kunne ikke reagere fordi noe gikk galt"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)
