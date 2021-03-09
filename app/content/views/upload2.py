from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


from app.common.permissions import IsMember
from rest_framework.parsers import MultiPartParser


class UploadView(APIView):
    parser_classes = (MultiPartParser, )
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        print(request.data)
        print("\n\n\n")
        return Response(
            {"detail": "Filen ble lastet opp"},
            status=status.HTTP_200_OK,
        )