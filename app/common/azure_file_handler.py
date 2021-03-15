import os
import uuid

from azure.storage.blob import BlobServiceClient, ContentSettings
from sentry_sdk import capture_exception

from app.common.file_handler import FileHandler


class AzureFileHandler(FileHandler):
    def __init__(self, blob):
        self.blob = blob

    def get_or_create_container(self, name="default"):
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        container = blob_service_client.get_container_client(name)
        if container.exists():
            return container

        container = blob_service_client.create_container(name, public_access="blob")
        return container

    def uploadBlob(self):
        "Uploads the given blob to Azure and returns a url to the blob"
        self.checkBlobSize()
        containerName = self.getContainerNameFromBlob()
        container = self.get_or_create_container(containerName)

        blob_name = f"{uuid.uuid4()}{self.getBlobName()}"
        content_settings = (
            ContentSettings(self.blob.content_type) if self.blob.content_type else None
        )

        blob_client = container.get_blob_client(blob_name)
        blob_client.upload_blob(data=self.blob, content_settings=content_settings)
        if blob_client.url:
            return blob_client.url
        raise ValueError("Noe gikk galt under filopplastningen")
