from rest_framework import serializers

from app.common.azure_file_handler import AzureFileHandler
from app.common.serializers import BaseModelSerializer
from app.files.models import File
from app.files.models.user_gallery import UserGallery


class FileSerializer(BaseModelSerializer):
    class Meta:
        model = File
        fields = (
            "id",
            "title",
            "url",
            "description",
            "created_at",
            "updated_at",
        )


class CreateFileSerializer(BaseModelSerializer):
    class Meta:
        model = File
        fields = (
            "title",
            "url",
            "description",
        )

    def create(self, validated_data):
        user = self.context["request"].user

        gallery = UserGallery.objects.get(author=user)

        if not gallery:
            raise serializers.ValidationError("No gallery found for user.")

        if gallery.files.count() >= 50:
            raise serializers.ValidationError("Gallery is full.")

        validated_data["gallery"] = gallery

        file_instance = super().create(validated_data)

        return file_instance


class UpdateFileSerializer(BaseModelSerializer):
    file = serializers.FileField(required=False)

    class Meta:
        model = File
        fields = (
            "title",
            "url",
            "description",
            "file",
        )


class DeleteFileSerializer(BaseModelSerializer):
    class Meta:
        model = File

    def delete(self, instance):
        azure_handler = AzureFileHandler(url=instance.url)
        azure_handler.deleteBlob()

        super().delete(instance)

        return f"Fil: '{instance.title}' har blitt slettet."
