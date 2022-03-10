from abc import ABC, abstractmethod


class FileHandler(ABC):

    SIZE_10_MB = 10000000

    @abstractmethod
    def __init__(self, blob=None):
        self.blob = blob

    @abstractmethod
    def get_or_create_container(self, name="default"):
        pass

    def getBlobName(self):
        return self.blob.name if self.blob.name else ""

    def getContainerNameFromBlob(self):
        return (
            "".join(e for e in self.blob.content_type if e.isalnum())
            if self.blob.content_type
            else None
        )

    def checkBlobSize(self):
        if self.blob.size > self.SIZE_10_MB:
            raise ValueError("Filen kan ikke være større enn 10 MB")

    @abstractmethod
    def uploadBlob(self):
        pass


def replace_file(instance_image, validated_data_image):
    from django.conf import settings

    from sentry_sdk import capture_exception

    from app.common.azure_file_handler import AzureFileHandler

    if instance_image and instance_image != validated_data_image:
        if settings.AZURE_BLOB_STORAGE_NAME in instance_image:
            try:
                AzureFileHandler(url=instance_image).deleteBlob()
            except Exception as e:
                capture_exception(e)
