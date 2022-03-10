from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.gallery.filters.album import AlbumFilter
from app.gallery.models.album import Album
from app.gallery.serializers.album import AlbumSerializer


class AlbumViewSet(BaseViewSet):
    serializer_class = AlbumSerializer
    queryset = Album.objects.all()
    permission_classes = [BasicViewPermission]
    lookup_field = "slug"
    pagination_class = BasePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AlbumFilter
    search_fields = ["title", "description"]

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({"detail": "Galleriet ble slettet"}, status=status.HTTP_200_OK)
