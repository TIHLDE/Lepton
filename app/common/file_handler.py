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


def replace_file(instance, validated_data):
    from django.conf import settings

    from app.common.azure_file_handler import AzureFileHandler

    assert hasattr(instance, "image") and "image" in validated_data
    if instance.image != validated_data["image"] and not settings.DEBUG:
        if settings.BLOB_STORAGE_NAME in instance.image:
            AzureFileHandler(url=instance.image).deleteBlob()
