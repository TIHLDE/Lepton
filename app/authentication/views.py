from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.authentication.exceptions import APIAuthUserDoesNotExist
from app.authentication.serializers import AuthSerializer
from app.content.models.user import User


@api_view(["POST"])
def login(request):
    serializer = AuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"detail": "Noe er feil i brukernavnet eller passordet ditt"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user_id = serializer.data["user_id"]
    password = serializer.data["password"]

    user = _try_to_get_user(user_id=user_id)

    if user.check_password(password):
        if user.is_TIHLDE_member:
            try:
                token = Token.objects.get(user_id=user_id).key
                return Response({"token": token}, status=status.HTTP_200_OK)
            except Token.DoesNotExist as token_not_exist:
                capture_exception(token_not_exist)

        return Response(
            {"detail": "Du må aktiveres som TIHLDE-medlem før du kan logge inn"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    else:
        return Response(
            {"detail": "Brukernavnet eller passordet ditt var feil"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


def _try_to_get_user(user_id):
    try:
        return User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        raise APIAuthUserDoesNotExist
