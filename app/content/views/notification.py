from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import NotificationPermission
from app.content.models import Notification
from app.content.serializers import (
    NotificationSerializer,
    UpdateNotificationSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ Get the notifications """

    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = (NotificationPermission,)
    pagination_class = BasePagination

    def get_queryset(self):
        if hasattr(self, "action") and self.action == "list":
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def update(self, request, pk):
        notification = get_object_or_404(Notification, id=pk)
        self.check_object_permissions(self.request, notification)
        serializer = UpdateNotificationSerializer(notification, data=request.data)
        if serializer.is_valid():
            notification = serializer.save()
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK,)
        return Response(
            {"detail": ("Kunne ikke oppdatere varslet")},
            status=status.HTTP_403_FORBIDDEN,
        )
