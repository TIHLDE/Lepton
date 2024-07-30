from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from app.content.serializers import FeideUserCreateSerializer, DefaultUserSerializer
from app.content.exceptions import FeideError


@api_view(["POST"])
def register_with_feide(request):
    """Register user with Feide credentials"""
    try:
        serializer = FeideUserCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.create(serializer.data)
            return Response(
                {"detail": DefaultUserSerializer(user).data},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        if isinstance(e, FeideError):
            return Response(
                {"detail": e.message},
                status=e.status_code,
            )

        return Response(
            {"detail": "Det skjedde en feil på serveren"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
