import os
import uuid

from azure.storage.blob import BlobServiceClient, ContentSettings
from sentry_sdk import capture_exception


def get_container_or_create_if_not_exist(name):
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container = blob_service_client.get_container_client(name)
    if container.exists:
        return container
    try:
        container = blob_service_client.create_container(name, public_access="blob")
        return container
    except Exception as e:
        print(f"Error: {e}")


def getBlobName(blob) -> str:
    return blob.name if blob.name != None else ""


def getContentSettings(blob) -> ContentSettings:
    return ContentSettings(blob.content_type) if blob.content_type != None else None


def uploadBlob(blob, container="default") -> str:
    "Uploads the given blob to Azure and returns a url to the blob"
    try:
        container = get_container_or_create_if_not_exist(container)

        blob_name = f"{uuid.uuid4()}{getBlobName(blob)}"

        blob_client = container.get_blob_client(blob_name)
        blob_client.upload_blob(data=blob, content_settings=getContentSettings(blob))
        return blob_client.url
    except Exception as e:
        capture_exception(e)
        return None
