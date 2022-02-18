from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets

from app.badge.filters.badge import BadgeFilter
from app.badge.models import Badge
from app.badge.serializers import BadgeSerializer
from app.common.mixins import ActionMixin, LoggingViewSetMixin
from app.common.pagination import BasePagination
from app.common.permissions import IsMember
from app.util.utils import now


class BadgeViewSet(
    LoggingViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    ActionMixin,
):
    serializer_class = BadgeSerializer
    pagination_class = BasePagination
    permission_classes = [IsMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = BadgeFilter
    search_fields = [
        "title",
        "description",
    ]

    def get_queryset(self):
        return Badge.objects.filter(
            (Q(active_from__isnull=True) | Q(active_from__lte=now()))
            & (Q(active_to__isnull=True) | Q(active_to__lte=now()))
        )
