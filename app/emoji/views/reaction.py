from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.emoji.models.reaction import Reaction
from app.emoji.serializers.reaction import (
    ReactionCreateSerializer,
    ReactionSerializer,
    ReactionUpdateSerializer,
)


class ReactionViewSet(BaseViewSet):
    serializer_class = ReactionSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def create(self, request, *args, **kwargs):
        data = request.data
        if data["user"] != request.id:
            return Response(
                {"detail": "Du har ikke tillatelse til å lage reaksjon"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            serializer = ReactionCreateSerializer(
                data=data, context={"request": request}
            )
            if serializer.is_valid():
                super().perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(
                {"detail": "Klarte ikke lagre reaksjon"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *args, **kwargs):
        reaction = self.get_object()

        if reaction.user.user_id != request.id:
            return Response(
                {"detail": "Du har ikke tillatelse til å endre reaksjon"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            serializer = ReactionUpdateSerializer(
                reaction, data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                reaction = super().perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Klarte ikke lagre reaksjon"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_queryset(self):
        return Reaction.objects.all()

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)
