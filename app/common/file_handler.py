from abc import ABC, abstractmethod


class FileHandler(ABC):

    # Ensure that users don't upload very huge files
    SIZE_50_MB = 50_000_000

    @abstractmethod
    def __init__(self, blob=None):
        self.blob = blob

    @abstractmethod
    def get_or_create_container(self, name="default"):
        pass

    def get_blob_name(self):
        return self.blob.name if self.blob.name else ""

    def get_container_name_from_blob(self):
        return (
            "".join(e for e in self.blob.content_type if e.isalnum())
            if self.blob.content_type
            else "default"
        )

    def check_blob_size(self):
        if self.blob.size > self.SIZE_50_MB:
            raise ValueError("Filen kan ikke være større enn 50 MB")

    @abstractmethod
    def upload_blob(self):
        pass


def replace_file(instance_image, validated_data_image):
    from django.conf import settings

    from sentry_sdk import capture_exception

    from app.common.azure_file_handler import AzureFileHandler

    if instance_image and instance_image != validated_data_image:
        if settings.AZURE_BLOB_STORAGE_NAME in instance_image:
            try:
                AzureFileHandler(url=instance_image).delete_blob()
            except Exception as e:
                capture_exception(e)
