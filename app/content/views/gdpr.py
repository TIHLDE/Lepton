from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def gdpr(request):
    return Response(
        {"detail": "flag{505e04a7-780c-4a96-8bd2-6e436e4df4f5}"},
        status=status.HTTP_418_IM_A_TEAPOT,
    )
