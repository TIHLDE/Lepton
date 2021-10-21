from django.db.models import lookups
from app.util.models import OptionalImage
from rest_framework import viewsets

from app.common.permissions import BasicViewPermission
from app.gallery.models.picture import Album, Picture
from app.gallery.serializers.picture import AlbumSerializer, PictureSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    queryset = Album.objects.all()
    permission_classes= [BasicViewPermission]

class PictureViewSet(viewsets.ModelViewSet, OptionalImage):
    serializer_class = PictureSerializer
    queryset = Picture.objects.all()
    permission_classes = [BasicViewPermission]


