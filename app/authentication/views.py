from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from sentry_sdk import capture_exception

from app.common.permissions import IsDev, IsHS

from ..content.models.user import User
from .exceptions import APIAuthUserDoesNotExist
from .serializers import AuthSerializer, MakeUserSerializer


@api_view(["POST"])
def login(request):
    serializer = AuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"detail": _("Noe er feil i brukernavnet eller passordet ditt")},
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
            {"detail": _("Du må aktiveres som TIHLDE-medlem før du kan logge inn")},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    else:
        return Response(
            {"detail": _("Brukernavnet eller passordet ditt var feil")},
            status=status.HTTP_401_UNAUTHORIZED,
        )


def _try_to_get_user(user_id):
    try:
        return User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        raise APIAuthUserDoesNotExist


@api_view(["POST"])
@permission_classes([IsDev, IsHS])
def makeMember(request):
    # Serialize data and check if valid
    serializer = MakeUserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"detail": ("Invalid user_id")}, status=400)

    # Get username and password
    user_id = serializer.data["user_id"]

    user = User.objects.get(user_id=user_id)
    if user is not None:
        try:
            Token.objects.get(user_id=user_id)
            return Response({"detail": ("Already a TIHLDE member")}, status=400)
        except Token.DoesNotExist as token_not_exist:
            capture_exception(token_not_exist)
            Token.objects.create(user=user)
            return Response({"detail": ("New TIHLDE member added")}, status=200)
    else:
        return Response({"detail": ("Incorrect user_id")}, status=400)
