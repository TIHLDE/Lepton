from rest_framework import viewsets
from rest_framework.response import Response

from ..models import Notification
from ..permissions import NotificationPermission, is_admin_user
from ..serializers import NotificationSerializer, UpdateNotificationSerializer


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
                return Response({'detail': ('Notification successfully updated.')}, status=204)
        return Response({'detail': ('Could not perform notification update')}, status=400)

    def create(self, request):
        if is_admin_user(request):
            serializer = NotificationSerializer
            if request.all_users:
                # Create notifications for all users.
                return Response({'detail': ('Not implementet yet.')}, status=400)

            else:
                if serializer.is_valid():
                    serializer.save()
                    return Response({'detail': ('Notification(s) successfully created.')}, status=201)
        return Response({'detail': ('Not allowed to create notifications.')}, status=400)