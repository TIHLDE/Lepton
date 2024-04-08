from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.content.filters import MinuteFilter
from app.content.models import Minute
from app.content.serializers import (
    MinuteCreateSerializer,
    MinuteListSerializer,
    MinuteSerializer,
    MinuteUpdateSerializer,
)


class MinuteViewSet(BaseViewSet):
    serializer_class = MinuteSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination
    queryset = Minute.objects.all()

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = MinuteFilter
    search_fields = [
        "title",
        "author__first_name",
        "author__last_name",
        "author__user_id",
    ]

    def get_serializer_class(self):
        if hasattr(self, "action") and self.action == "list":
            return MinuteListSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = MinuteCreateSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            minute = super().perform_create(serializer)
            serializer = MinuteSerializer(minute)
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
            serializer = MinuteSerializer(minute)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "The minute was deleted"}, status=status.HTTP_200_OK)
