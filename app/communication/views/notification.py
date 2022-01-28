from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.communication.models import Notification
from app.communication.serializers import (
    NotificationSerializer,
    UpdateNotificationSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ Get the notifications """

    serializer_class = NotificationSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination

    def get_queryset(self):
        return self.request.user.notifications.all().order_by("-created_at")

    def update(self, request, pk):
        notification = get_object_or_404(Notification, id=pk)
        self.check_object_permissions(self.request, notification)
        serializer = UpdateNotificationSerializer(
            notification, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            notification = serializer.save()
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK,)
        return Response(
            {"detail": ("Kunne ikke oppdatere varslet")},
            status=status.HTTP_403_FORBIDDEN,
        )
