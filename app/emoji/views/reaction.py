from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models.news import News
from app.emoji.models.reaction import Reaction
from app.emoji.serializers.reaction import ReactionSerializer


class ReactionViewSet(BaseViewSet):

    serializer_class = ReactionSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def create(self, request, *args, **kwargs):
        content_type = request.data.get("content_type")

        if content_type == "news":
            content_object = get_object_or_404(News, id=request.data.get("object_id"))
            if not content_object.emojis_allowed:
                return Response(
                    {"detail": "Reaksjoner er ikke tillatt her."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Content type er ikke støttet"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ReactionSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            super().perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"detail": "Du har ikke tillattelse til å reagere"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        content_type = request.data.get("content_type")
        if content_type == "news":
            content_object = get_object_or_404(News, id=request.data.get("object_id"))

            if not content_object.emojis_allowed:
                return Response(
                    {"detail": "Reaksjoner er ikke tillatt her."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "Content type er ikke støttet"},
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
            {"detail": "Du har ikke tillatelse til å endre reaksjon"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get_queryset(self):
        queryset = Reaction.objects.all()
        return queryset

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)
