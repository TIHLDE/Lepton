from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.apikey.models.key import ApiKey
from app.apikey.util import is_valid_uuid
from app.common.azure_file_handler import AzureFileHandler


@api_view(["POST"])
def upload(request):
    """Method for uploading files to Azure Blob Storage, only allowed with a valid API key"""
    try:
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return Response(
                {"detail": "API nøkkel mangler"},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_valid_api_key = is_valid_uuid(api_key)
        if not is_valid_api_key:
            return Response(
                {"detail": "API nøkkel er ikke riktig format. Den må være UUID"},
                status=status.HTTP_403_FORBIDDEN,
            )

        valid_api_key = ApiKey.objects.filter(key=api_key).first()

        if not valid_api_key:
            return Response(
                {"detail": "Ugyldig API nøkkel"},
                status=status.HTTP_403_FORBIDDEN,
            )

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
