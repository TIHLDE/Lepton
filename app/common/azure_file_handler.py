import os
import re
import uuid

from azure.storage.blob import BlobServiceClient, ContentSettings

from app.common.file_handler import FileHandler


class AzureFileHandler(FileHandler):
    def __init__(self, blob=None, url=None):
        self.blob = blob
        self.url = url
        if url:
            data = self.getContainerAndNameFromUrl()
            self.containerName = data[0]
            self.blobName = data[1]

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

    def getContainerAndNameFromUrl(self):
        import urllib.parse

        url = urllib.parse.unquote(self.url)
        # fmt: off
        return re.sub("\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*/", "", url).split("/")  # noqa: W605
        # fmt: on

    def uploadBlob(self):
        "Uploads the given blob to Azure and returns a url to the blob"
        if not self.blob:
            raise ValueError("Du må sende med en blob for som skal lastes opp")

        self.checkBlobSize()
        containerName = self.getContainerNameFromBlob()
        container = self.get_or_create_container(containerName)

        blob_name = f"{uuid.uuid4()}{self.getBlobName()}"
        content_settings = ContentSettings(
            content_type=self.blob.content_type if self.blob.content_type else None,
            cache_control="public,max-age=2592000",
        )

        blob_client = container.get_blob_client(blob_name)
        blob_client.upload_blob(data=self.blob, content_settings=content_settings)
        if blob_client.url:
            return blob_client.url
        raise ValueError("Noe gikk galt under filopplastningen")

    def deleteBlob(self):
        "Delete a blob by it's url"
        if not self.blobName and not self.containerName:
            raise ValueError("Du kan ikke slette en blob uten en url")

        container = self.get_or_create_container(self.containerName)
        container.delete_blob(self.blobName)
        return f"{self.blobName} har blitt slettet fra {self.containerName}"
