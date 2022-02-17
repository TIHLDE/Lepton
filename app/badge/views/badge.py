from rest_framework import mixins, viewsets
from rest_framework.decorators import action

from app.badge.models import Badge, BadgeCategory
from app.badge.serializers import BadgeCategorySerializer, BadgeSerializer
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

    @action(detail=False, methods=["get"], url_path="categories")
    def get_categories(self, request, *args, **kwargs):
        return self.paginate_response(
            data=BadgeCategory.objects.all(),
            serializer=BadgeCategorySerializer,
            context={"request": request},
        )
