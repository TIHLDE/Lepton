from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
load_dotenv()


def create_container(name):
    try:
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_service_client.create_container(name)
    except ResourceExistsError:
        #TODO:
        #Better error handling
        print("Container already exists.")
    except Exception as e:
        print(f"Error: {e}")
