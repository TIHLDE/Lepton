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
    queryset = Reaction.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = ReactionCreateSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            super().perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        reaction = self.get_object()
        serializer = ReactionUpdateSerializer(
            reaction, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            super().perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Reaksjonen ble slettet"}, status=status.HTTP_200_OK)
