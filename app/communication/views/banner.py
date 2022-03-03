from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from app.common.mixins import ActionMixin
from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission, IsHS
from app.common.viewsets import BaseViewSet
from app.communication.models.banner import Banner
from app.communication.serializers.banner import BannerSerializer
from app.util.utils import now


class BannerViewSet(BaseViewSet, ActionMixin):
    serializer_class = BannerSerializer
    pagination_class = BasePagination
    queryset = Banner.objects.all()
    permission_classes = [IsHS]

    @action(
        detail=False,
        methods=["get"],
        url_path="today",
        permission_classes=[BasicViewPermission],
    )
    def get_visible_banner(self, request):
        banner = Banner.objects.filter(
            Q(visible_from__lte=now()) & Q(visible_until__gte=now())
        )
        if not banner:
            return Response(
                {"detail": "Ingen bannere i dag"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = BannerSerializer(
            banner.first(), context={"request": request}, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
