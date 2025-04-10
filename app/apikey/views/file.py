from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.apikey.util import check_api_key
from app.common.azure_file_handler import AzureFileHandler


@api_view(["POST"])
@check_api_key
def upload(request):
    """Method for uploading files to Azure Blob Storage, only allowed with a valid API key.

    Body should contain:
    - 'container_name': The name of the container to upload the file to.
    - 'FILES': The file to upload.

    The header should contain:
    - 'x-api_key': A key for validating access.
    """
    try:
        has_multiple_files = len(request.FILES) > 1
        if has_multiple_files:
            return Response(
                {"detail": "Du kan ikke sende med flere filer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        no_files = len(request.FILES) < 1
        if no_files:
            return Response(
                {"detail": "Du må sende med en fil i FILE"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        container_name = request.data.get("container_name")

        key = list(request.FILES.keys())[0]
        blob = request.FILES[key]
        url = AzureFileHandler(blob).upload_blob(container_name=container_name)
        return Response(
            {"url": url},
            status=status.HTTP_200_OK,
        )

    except Exception:
        return Response(
            {"detail": "En feil oppstod under behandlingen av forespørselen."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
