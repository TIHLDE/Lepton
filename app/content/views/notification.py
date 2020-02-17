from rest_framework import viewsets
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from ..models import User, Notification
from ..serializers import NotificationSerializer, UserSerializer
from ..permissions import IsMember, IsDev, IsHS, get_user_id

class NotificationViewSet(viewsets.ModelViewSet):
    """ Get the notifications """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsDev | IsHS]

    def get_permissions(self):
        """ Allow memvers to mark own notifications as read """
        if self.request.method in ['update', 'retrieve']:
            self.permission_classes = [IsMember]

        return super(NotificationViewSet, self).get_permissions()

    def list(self, request, user_id):
        return Response({'detail': 'Not authenticated'})

    def retrieve(self, request,user_id, pk, *args, **kwargs):
        """ Get own notifications """
        notification = 0
        try:
            notification = Notification.objects.get(pk=pk)

        except ObjectDoesNotExist:
            return Response({'detail': 'Object doesn\'t exist!'})
        
        serializer = NotificationSerializer(notification)
        pk_user_id = get_user_id(request)
        if pk_user_id == user_id:
            return Response(serializer.data)
        else: 
            return Response({'detail': 'No access to this notifcation'})
