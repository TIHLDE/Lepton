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

    def getBlobName(self):
        return self.blob.name if self.blob.name else ""

    def getContainerNameFromBlob(self):
        return (
            "".join(e for e in self.blob.content_type if e.isalnum())
            if self.blob.content_type
            else None
        )

    def checkBlobSize(self):
        if self.blob.size > self.SIZE_50_MB:
            raise ValueError("Filen kan ikke være større enn 50 MB")

    @abstractmethod
    def uploadBlob(self):
        pass
