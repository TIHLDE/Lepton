from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.common.azure_file_handler import AzureFileHandler
from app.common.permissions import IsMember


@api_view(["POST"])
@permission_classes([IsMember])
def upload(request):
    """Method for uploading files til Azure Blob Storage, only allowed for members"""
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

        key = list(request.FILES.keys())[0]
        blob = request.FILES[key]
        url = AzureFileHandler(blob).uploadBlob()
        return Response(
            {"url": url},
            status=status.HTTP_200_OK,
        )

    except ValueError as value_error:
        return Response(
            {"detail": str(value_error)},
            status=status.HTTP_400_BAD_REQUEST,
        )
