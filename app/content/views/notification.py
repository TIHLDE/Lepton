from rest_framework import status, viewsets
from rest_framework.response import Response

from app.common.permissions import NotificationPermission, is_admin_user
from app.content.models import Notification
from app.content.serializers import (
    NotificationSerializer,
    UpdateNotificationSerializer,
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ Get the notifications """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (NotificationPermission,)

    def update(self, request, pk):
        notification = Notification.objects.get(id=pk)
        if request.user == notification.user or is_admin_user(request):
            serializer = UpdateNotificationSerializer(notification, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"detail": serializer.data}, status=status.HTTP_200_OK,)
        return Response(
            {"detail": ("Kunne ikke oppdatere varslet")},
            status=status.HTTP_403_FORBIDDEN,
        )
