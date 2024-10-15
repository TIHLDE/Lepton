from django.http import Http404
from rest_framework import status
from rest_framework.response import Response

from app.common.permissions import BasicViewPermission
from app.common.viewsets import BaseViewSet
from app.files.models.file import File
from app.files.serializers.file import (
    CreateFileSerializer,
    FileSerializer,
    UpdateFileSerializer,
)


class FileViewSet(BaseViewSet):
    serializer_class = FileSerializer
    permission_classes = [BasicViewPermission]
    queryset = File.objects.all()

    def retrieve(self, request, *_args, **_kwargs):
        """Retrieves a specific file by id"""
        try:
            file = self.get_object()
            serializer = FileSerializer(file, context={"request": request}, many=False)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except File.DoesNotExist:
            return Response(
                {"detail": "Filen eksisterer ikke"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, *_args, **_kwargs):
        """Updates a specific file by id"""
        try:
            file = self.get_object()

            serializer = UpdateFileSerializer(
                file, data=request.data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response(
                {"detail": "Filen eksisterer ikke."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request, *args, **kwargs):
        """Creates a file"""
        serializer = CreateFileSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            file = super().perform_create(serializer)
            return_serializer = CreateFileSerializer(file)
            return Response(data=return_serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *_args, **_kwargs):
        """Deletes a specific file by id"""
        try:
            file = self.get_object()
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except File.DoesNotExist:
            return Response(
                {"detail": "Filen eksisterer ikke"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
