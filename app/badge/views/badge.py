from rest_framework import viewsets

from app.badge.models import Badge
from app.badge.serializers import BadgeSerializer
from app.common.pagination import BasePagination
from app.common.permissions import IsHS


class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsHS]
    http_method_names = ["get", "post"]
    pagination_class = BasePagination
