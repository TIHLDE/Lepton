from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission, IsHS
from app.common.viewsets import BaseViewSet
from app.communication.models.banner import Banner
from app.communication.serializers.banner import BannerSerializer


class BannerViewSet(BaseViewSet, ActionMixin):
    serializer_class = BannerSerializer
    pagination_class = BasePagination
    queryset = Banner.objects.all()
    permission_classes = [IsHS]

    @action(
        detail=False,
        methods=["get"],
        url_path="visible",
        permission_classes=[BasicViewPermission],
    )
    def get_visible_banner(self, request):
        banners = Banner.objects.visible()
        if not banners:
            return Response(
                {"detail": "Ingen synlige bannere"}, status=status.HTTP_404_NOT_FOUND
            )
        elif banners.count() > 1:
            return Response({"detail": "Bare et banner skal være synlig"})

        serializer = BannerSerializer(
            banners.first(), context={"request": request}, many=False
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
