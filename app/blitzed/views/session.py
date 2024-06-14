from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.blitzed.models.session import Session
from app.blitzed.serializers.session import SessionSerializer
from app.common.permissions import BasicViewPermission


class SessionViewset(ModelViewSet):
    queryset = Session.objects.all().order_by("-start_time")
    serializer_class = SessionSerializer
    permission_classes = [BasicViewPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Sesjonen ble slettet"}, status=status.HTTP_200_OK)
