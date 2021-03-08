from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
load_dotenv()


def create_container(name):
    try:
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        result = blob_service_client.create_container(name)
        print(result)
    except Exception as e:
        print("Hallo")
        # TODO:
        # Better exception handling than this silly little print
        print(e)


create_container("Max")
