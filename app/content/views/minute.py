from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.models import Minute
from app.content.serializers import (
    MinuteCreateSerializer,
    MinuteSerializer,
    MinuteUpdateSerializer,
)


class MinuteViewSet(BaseViewSet):
    serializer_class = MinuteSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination
    queryset = Minute.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = MinuteCreateSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            super().perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        minute = self.get_object()
        serializer = MinuteUpdateSerializer(
            minute, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            minute = super().perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "The minute was deleted"}, status=status.HTTP_200_OK)
