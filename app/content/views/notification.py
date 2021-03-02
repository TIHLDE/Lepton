from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import NotificationPermission, get_user_id
from app.content.models import Notification, User
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
        user = get_object_or_404(User, user_id=get_user_id(self.request))
        return self.queryset.filter(user=user)

    def update(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        serializer = UpdateNotificationSerializer(notification, data=request.data)
        if serializer.is_valid():
            notification = serializer.save()
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK,)
        return Response(
            {"detail": ("Kunne ikke oppdatere varslet")},
            status=status.HTTP_403_FORBIDDEN,
        )
