from rest_framework import viewsets

from app.common.permissions import BasicViewPermission
from app.content.models import Warning
from app.content.serializers import WarningSerializer


class WarningViewSet(viewsets.ModelViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [BasicViewPermission]
