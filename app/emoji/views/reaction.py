from django.contrib.contenttypes.models import ContentType
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
        content_type_str = request.data.get("content_type")
        try:
            content_type = ContentType.objects.get(model=content_type_str)
        except ContentType.DoesNotExist:
            return Response(
                {"detail": "Fant ikke content type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if content_type_str == "news":
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
        try:
            request.data["content_type"] = content_type.id
            serializer = ReactionSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {"detail": "Du har ikke tillattelse til å reagere"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError:
            return Response(
                {"detail": "Klarte ikke lagre reaksjon"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        content_type_str = request.data.get("content_type")
        try:
            content_type = ContentType.objects.get(model=content_type_str)
        except ContentType.DoesNotExist:
            return Response(
                {"detail": "Fant ikke content type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if content_type_str == "news":
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

        try:
            reaction = self.get_object()
            request.data["content_type"] = content_type.id
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
        except ValueError:
            return Response(
                {"detail": "Klarte ikke lagre reaksjon"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_queryset(self):
        queryset = Reaction.objects.all()
        return queryset

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)
