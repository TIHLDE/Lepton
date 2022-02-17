from rest_framework import mixins, viewsets

from app.badge.models import Badge
from app.badge.serializers import BadgeSerializer
from app.common.mixins import ActionMixin, LoggingViewSetMixin
from app.common.pagination import BasePagination


class BadgeViewSet(
    LoggingViewSetMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    ActionMixin,
):
    queryset = Badge.objects.public()
    serializer_class = BadgeSerializer
    pagination_class = BasePagination
