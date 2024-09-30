from app.common.azure_file_handler import AzureFileHandler
from app.common.serializers import BaseModelSerializer
from app.files.models import File
from app.files.models.gallery import Gallery


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

        gallery = Gallery.objects.get(author=user)

        validated_data["gallery"] = gallery

        file_instance = super().create(validated_data)

        return file_instance


class DeleteFileSerializer(BaseModelSerializer):
    class Meta:
        model = File

    def delete(self, instance):
        azure_handler = AzureFileHandler(url=instance.url)
        azure_handler.deleteBlob()

        super().delete(instance)

        return f"Fil: '{instance.title}' har blitt slettet."
