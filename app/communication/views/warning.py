from django.core.cache import cache

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.communication.models import Warning
from app.communication.serializers import WarningSerializer


class WarningViewSet(BaseViewSet):

    queryset = Warning.objects.all()
    serializer_class = WarningSerializer
    permission_classes = [BasicViewPermission]

    def get_queryset(self):
        CACHE_KEY = "warnings_cache"
        CACHE_WARNINGS_SECONDS = 60 * 10
        queryset = cache.get(CACHE_KEY)
        if queryset is None:
            queryset = self.queryset
            cache.set(CACHE_KEY, queryset, CACHE_WARNINGS_SECONDS)
        return queryset
