from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import IsMember
from app.common.viewsets import BaseViewSet
from app.files.models import Gallery
from app.files.serializers import GallerySerializer


class GalleryView(BaseViewSet):
    serializer_class = GallerySerializer
    permission_classes = [IsMember]

    def retrieve(self, request, *_args, **_kwargs):
        """Retrieve all files in gallery"""
        try:
            files = Gallery.get_all_files(request.user)
            serializer = GallerySerializer(files, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Gallery.DoesNotExist:
            return Response(
                {"detail": "Galleriet finnes ikke"},
                status=status.HTTP_400_BAD_REQUEST,
            )
