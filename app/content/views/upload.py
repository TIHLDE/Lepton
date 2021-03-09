import os
from rest_framework import status

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from app.common.permissions import IsMember
from app.common.azure_blob_storage_handler import uploadBlob

from sentry_sdk import capture_exception


@api_view(["POST"])
@permission_classes([IsMember])
def upload(request):
    """ Method for accepting company interest forms from the company page """
    try:
        blob = request.data["file"]
        print(request.data["file"])
        url = uploadBlob(blob)
        return Response(
            {"detail": "Filen ble lastet opp", "url": url},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        capture_exception(e)
        raise
