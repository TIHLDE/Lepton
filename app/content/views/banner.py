from rest_framework import viewsets

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.content.models.banner import Banner
from app.content.serializers.banner import BannerSerializer


class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [BasicViewPermission]
    pagination_class = BasePagination
