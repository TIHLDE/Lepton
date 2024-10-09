from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.files.models.user_gallery import UserGallery
from app.files.serializers.user_gallery import UserGallerySerializer


class UserGalleryViewSet(BaseViewSet):
    serializer_class = UserGallerySerializer
    permission_classes = [BasicViewPermission]
    queryset = UserGallery.objects.all()

    def retrieve(self, request, *_args, **_kwargs):
        """Retrieve all files in gallery"""
        try:
            files = UserGallery.get_all_files(request.user)
            serializer = UserGallerySerializer(files, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserGallery.DoesNotExist:
            return Response(
                {"detail": "Galleriet finnes ikke"},
                status=status.HTTP_400_BAD_REQUEST,
            )
