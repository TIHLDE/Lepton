from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.common.azure_file_handler import AzureFileHandler
from app.common.permissions import IsMember
from app.common.viewsets import BaseViewSet


class UploadView(BaseViewSet):
    serializer_class = UploadSerializer
    permission_classes = [IsMember]

    def retrieve(self, request, *_args, **_kwargs):
        pass

    def update(self, request, *_args, **_kwargs):
        pass

    def create(self, request, *_args, **_kwargs):
        pass
