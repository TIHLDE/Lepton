from rest_framework import viewsets

from app.common.pagination import BasePagination
from app.common.permissions import BasicViewPermission
from app.gallery.models.album import Album
from app.gallery.serializers.album import AlbumSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    queryset = Album.objects.all()
    permission_classes = [BasicViewPermission]
    lookup_field = "slug"
    pagination_class = BasePagination
