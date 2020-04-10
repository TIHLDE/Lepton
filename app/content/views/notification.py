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
            try:
                if 'all_users' in request.data and request.data['all_users']:
                    # Create notifications for all users.
                    newData = [
                        {
                            'user': users.user_id,
                            'message': request.data['message'],
                            'read': False
                        } for users in User.objects.filter()
                    ]

                    serializer = NotificationSerializer(data=newData, many=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'detail': ('Notification(s) successfully created.')}, status=201)
                    else:
                        return Response({'detail': ('Invalid data sent in.')}, status=400)

                else:
                    serializer = NotificationSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'detail': ('Notification(s) successfully created.')}, status=201)
                    else:
                        return Response({'detail': ('Invalid data sent in.')}, status=400)
            except:
                return Response({'detail': ('Missing fields or invalid data.')}, status=400)

        return Response({'detail': ('Not allowed to create notifications.')}, status=401)