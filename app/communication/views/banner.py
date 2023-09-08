from django_filters import BooleanFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework.filterset import FilterSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.communication.models.banner import Banner
from app.communication.serializers.banner import BannerSerializer
from app.util.utils import now


class BannerFilter(FilterSet):
    is_visible = BooleanFilter(method="filter_isVisible")
    is_expired = BooleanFilter(method="filter_isExpired")

    class Meta:
        model = Banner
        fields = ["is_visible", "is_expired"]

    def filter_isVisible(self, queryset, name, value):
        if value:
            return queryset.filter(is_visible=True)
        return queryset

    def filter_isExpired(self, queryset, name, value):
        if value:
            return queryset.filter(is_expired=True)
        return queryset


class BannerViewSet(BaseViewSet):
    serializer_class = BannerSerializer
    pagination_class = BasePagination
    queryset = Banner.objects.all()
    permission_classes = [BasicViewPermission]

    filter_backends = [DjangoFilterBackend]
    filterset_class = BannerFilter

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Banneret ble slettet"}, status=status.HTTP_200_OK)

    def get_queryset(self):
        return self.queryset.order_by("-visible_from")

    @action(
        detail=False,
        methods=["get"],
        url_path="visible",
    )
    def visible(self, request):
        banner = Banner.objects.filter(
            visible_from__lte=now(), visible_until__gte=now()
        )
        serializer = BannerSerializer(banner, context={"request": request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
