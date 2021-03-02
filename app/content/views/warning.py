from rest_framework import viewsets

from app.common.permissions import IsDev, IsNoK
from app.content.models import Warning
from app.content.serializers import WarningSerializer
from dry_rest_permissions.generics import DRYPermissions


class WarningViewSet(viewsets.ModelViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [DRYPermissions]
