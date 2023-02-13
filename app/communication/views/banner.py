from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from app.communication.filters.banner import BannerFilter
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.communication.models.banner import Banner
from app.communication.serializers.banner import BannerSerializer
from app.util.utils import now, yesterday, midday


class BannerViewSet(BaseViewSet):
    serializer_class = BannerSerializer
    pagination_class = BasePagination
    queryset = Banner.objects.all()
    permission_classes = [BasicViewPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = BannerFilter
    ordering_fields = ["visible_from", "visible_until"]
    ordering = ["-visible_from"]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Banneret ble slettet"}, status=status.HTTP_200_OK)

    def get_queryset(self):
        midday_yesterday = midday(yesterday())
        midday_today = midday(now())
        time = midday_today if midday_today < now() else midday_yesterday
        expired = self.request.query_params.get("expired", "false").lower() == "true"
        if expired:
            return self.queryset.filter(visible_from__lte=time).order_by("-visible_from")
        return self.queryset.filter(visible_until__gte=time)

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
