from rest_framework import viewsets

from ..models import Warning
from ..permissions import IsDev, IsNoK
from ..serializers import WarningSerializer


class WarningViewSet(viewsets.ModelViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [IsDev | IsNoK]
