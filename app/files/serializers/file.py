from rest_framework import serializers

from app.common.azure_file_handler import AzureFileHandler
from app.common.serializers import BaseModelSerializer
from app.constants import MAX_GALLERY_SIZE
from app.files.exceptions import GalleryIsFull, NoGalleryFoundForUser
from app.files.models import File
from app.files.models.user_gallery import UserGallery


class FileSerializer(BaseModelSerializer):
    class Meta:
        model = File
        fields = (
            "id",
            "title",
            "description",
            "file",
            "created_at",
            "updated_at",
        )


class CreateFileSerializer(BaseModelSerializer):
    class Meta:
        model = File
        fields = (
            "title",
            "description",
            "file",
        )

    def create(self, validated_data):
        user = self.context["request"].user

        gallery = UserGallery.objects.filter(author=user).first()

        if not gallery:
            raise NoGalleryFoundForUser()

        if gallery.files.count() >= MAX_GALLERY_SIZE:
            raise GalleryIsFull()

        validated_data["gallery"] = gallery

        file_instance = super().create(validated_data)

        return file_instance


class UpdateFileSerializer(BaseModelSerializer):

    class Meta:
        model = File
        fields = (
            "title",
            "description",
            "file",
        )


class DeleteFileSerializer(BaseModelSerializer):
    class Meta:
        model = File

    def delete(self, instance):
        azure_handler = AzureFileHandler(url=instance.url)
        azure_handler.deleteBlob()

        return super().delete(instance)
