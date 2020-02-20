from rest_framework import viewsets
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from ..models import User, Notification
from ..serializers import NotificationSerializer, UserSerializer
from ..permissions import NotificationPermission

class NotificationViewSet(viewsets.ModelViewSet):
    """ Get the notifications """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (NotificationPermission,)