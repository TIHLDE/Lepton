from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.communication.models.banner import Banner
from app.communication.serializers.banner import BannerSerializer
from app.util.utils import now


class BannerViewSet(BaseViewSet):
    serializer_class = BannerSerializer
    pagination_class = BasePagination
    queryset = Banner.objects.all()
    permission_classes = [BasicViewPermission]

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
