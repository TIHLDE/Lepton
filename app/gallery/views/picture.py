from rest_framework.response import Response
from app.common.permissions import BasicViewPermission
from os import write
from app.gallery import serializers
from app.gallery.models import Picture
from rest_framework import viewsets

from app.gallery.serializers import PictureSerializer


class PictureViewSet(viewsets.ModelViewSet):
    serializer_class = PictureSerializer
    queryset = Picture.objects.all()
    permission_classes = [BasicViewPermission]
    lookup_field = "title"

 


       