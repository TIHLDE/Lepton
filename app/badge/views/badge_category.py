from rest_framework import mixins, viewsets, filters

from app.badge.models import BadgeCategory
from app.badge.serializers import BadgeCategorySerializer
from app.common.mixins import ActionMixin, LoggingViewSetMixin
from app.common.pagination import BasePagination
from app.common.permissions import IsMember


class BadgeCategoryViewSet(
    LoggingViewSetMixin,
    viewsets.GenericViewSet,
    ActionMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = BadgeCategory.objects.all()
    serializer_class = BadgeCategorySerializer
    permission_classes = [IsMember]
    pagination_class = BasePagination
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
        "description",
    ]
