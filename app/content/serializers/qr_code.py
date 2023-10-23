from django.core.files import File
from rest_framework import serializers

from app.common.azure_file_handler import AzureFileHandler
from app.common.serializers import BaseModelSerializer
from app.content.models import QRCode


class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = ("id", "name", "created_at", "updated_at", "content")


class QRCodeCreateSerializer(BaseModelSerializer):
    class Meta:
        model = QRCode
        fields = (
            "name",
            "content",
        )
