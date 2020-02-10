from rest_framework import viewsets

from ..models import User, Notification
from ..serializers import NotificationSerializer
from ..permissions import IsDev, IsNoK

class NotificationViewSet(viewsets.ModelViewSet):
    """" Get the notifications """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsDev | IsNoK]
