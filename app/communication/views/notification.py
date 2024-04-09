from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.communication.models import Notification
from app.communication.serializers import (
    CreateNotificationSerializer,
    NotificationSerializer,
    UpdateNotificationSerializer,
)


class NotificationViewSet(BaseViewSet):
    """Get the notifications"""

    serializer_class = NotificationSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_queryset(self):
        return self.request.user.notifications.all().order_by("-created_at")

    def create(self, request):
        user = request.user
        serializer = CreateNotificationSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            notification = super().perform_create(serializer, user=user)
            serializer = NotificationSerializer(notification)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, pk):
        notification = get_object_or_404(Notification, id=pk)
        serializer = UpdateNotificationSerializer(
            notification, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            notification = super().perform_update(serializer)
            serializer = NotificationSerializer(notification)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": ("Kunne ikke oppdatere varslet")},
            status=status.HTTP_403_FORBIDDEN,
        )
