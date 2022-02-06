from app.common.azure_file_handler import AzureFileHandler


def test_get_getContainerAndNameFromUrl():
    container_name = "testcontainer"
    file_name = "testfile"
    handler = AzureFileHandler(
        url=f"https://tihldestorage.blob.core.windows.net/{container_name}/{file_name}"
    )
    data = handler.getContainerAndNameFromUrl()
    assert data[0] == container_name
    assert data[1] == file_name
