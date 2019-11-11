from rest_framework import viewsets

from ..models import Warning
from ..serializers import WarningSerializer
from ..permissions import IsDev


class WarningViewSet(viewsets.ModelViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [IsDev]
