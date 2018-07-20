from rest_framework import generics, status
from rest_framework.response import Response

from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .serializers import RefreshTokenBlacklistSerializer

class RefreshTokenBlacklistView(generics.GenericAPIView):
    """Invalidates a token pair by adding it to the blacklist."""
    serializer_class = RefreshTokenBlacklistSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(status=status.HTTP_200_OK)

