from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.badge.models import Badge, BadgeCategory
from app.badge.serializers import BadgeSerializer, BadgeCategorySerializer
from app.common.pagination import BasePagination
from app.common.mixins import LoggingViewSetMixin, ActionMixin


class BadgeViewSet(LoggingViewSetMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet, ActionMixin):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    pagination_class = BasePagination

    @action(detail=False, methods=["get"], url_path="categories")
    def get_categories(self, request, *args, **kwargs):
        return self.paginate_response(
            data=BadgeCategory.objects.all(),
            serializer=BadgeCategorySerializer,
            context={"request": request},
        )
