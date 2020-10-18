from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import viewsets, status
from rest_framework.response import Response

from app.content.models.notification import Notification
from app.content.models.user import User
from app.content.permissions import NotificationPermission, is_admin_user
from app.content.serializers.notification import NotificationSerializer, UpdateNotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (NotificationPermission,)

    def get_serializer_class(self, *args, **kwargs):
        if self.action == "update":
            return UpdateNotificationSerializer
        return NotificationSerializer

    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        if self._attempts_to_access_own_notification(notification) or is_admin_user(self.request):
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({'detail': serializer.data}, status=status.HTTP_200_OK)

        return Response({'detail': _('Cannot access this notification')}, status=status.HTTP_400_BAD_REQUEST)

    def _attempts_to_access_own_notification(self, notification):
        return self.request.user == notification.user

    def create(self, request, *args, **kwargs):
        notifications = request.data
        many = self._should_send_to_all_users()
        message = request.data.get("message")

        serializer = self.get_serializer(data=notifications, many=many)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            return Response({'detail': _('Missing fields or invalid data.')}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: not sure this works
        if many:
            notifications = Notification.objects.create_for_all_users(message)
        else:
            notifications = serializer.save()

        notification_serializer = NotificationSerializer(data=notifications, many=many)
        return Response({'detail': notification_serializer.data}, status=status.HTTP_201_CREATED)

    def _should_send_to_all_users(self):
        return 'all_users' in self.request.data and self.request.data.get('all_users')