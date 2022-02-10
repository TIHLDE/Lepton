from django.conf import settings

from app.common.azure_file_handler import AzureFileHandler


def test_get_getContainerAndNameFromUrl():
    container_name = "testcontainer"
    file_name = "testfile"
    handler = AzureFileHandler(
        url=f"https://{settings.AZURE_BLOB_STORAGE_NAME}/{container_name}/{file_name}"
    )
    data = handler.getContainerAndNameFromUrl()
    assert data[0] == container_name
    assert data[1] == file_name
