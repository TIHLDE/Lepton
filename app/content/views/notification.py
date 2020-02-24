from rest_framework import viewsets
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from ..models import User, Notification
from ..serializers import NotificationSerializer, UpdateNotificationSerializer, UserSerializer
from ..permissions import NotificationPermission, is_admin_user

class NotificationViewSet(viewsets.ModelViewSet):
    """ Get the notifications """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (NotificationPermission,)

    def update(self, request, pk):
        notification = Notification.objects.get(id=pk)
        if request.user == notification.user or is_admin_user(request):
            serializer = UpdateNotificationSerializer(notification, data=request.data)
            serializer.is_valid()
            serializer.save()
            return serializer.validated_data
        else:
            return Response({'detail': ('Could not perform notification update')}, status=400)