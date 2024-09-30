from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import IsMember
from app.common.viewsets import BaseViewSet
from app.files.models import Gallery
from files.serializers import FileSerializer, GallerySerializer, CreateFileSerializer


class FileView(BaseViewSet):
    serializer_class = FileSerializer
    permission_classes = [IsMember]

    def retrieve(self, request, *_args, **_kwargs):
        try:
            if not request.FILES or len(request.FILES) > 1 or len(request.FILES) == 0:
                return Response(
                    {"detail": "Du må sende én fil i FILE"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = FileSerializer.get_file_url_from_file(request.FILES)

            return Response(
                {"url": serializer.url},
                status=status.HTTP_200_OK,
            )
        except ValueError as value_error:
            return Response(
                {"detail": str(value_error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def update(self, request, *_args, **_kwargs):
        pass

    def create(self, request, *_args, **_kwargs):
        try:
            if not Gallery.has_gallery(request.user):
                GallerySerializer.create_gallery(request.user)

            if not request.FILES or len(request.FILES) > 1 or len(request.FILES) == 0:
                return Response(
                    {"detail": "Du må sende én fil i FILE"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = CreateFileSerializer.create_file(request.FILES, request.user)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as value_error:
            return Response(
                {"detail": str(value_error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

