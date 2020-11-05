from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.common.permissions import IsDev, IsHS

from ..content.models.user import User
from .serializers import AuthSerializer, MakeUserSerializer


@api_view(["POST"])
def login(request):
    # Serialize data and check if valid
    serializer = AuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"detail": ("Feil brukernavn eller passord")}, status=401)

    # Get username and password
    user_id = serializer.data["user_id"]
    password = serializer.data["password"]

    user = User.objects.get(user_id=user_id)
    if user.check_password(password):
        if user.is_TIHLDE_member:
            try:
                token = Token.objects.get(user_id=user_id).key
                return Response({"token": token}, status=200)
            except Token.DoesNotExist:
                return Response({"detail": ("Ikke aktivert TIHLDE medlem")}, status=401)
        else:
            return Response({"detail": ("Ikke aktivert TIHLDE medlem")}, status=401)
    else:
        return Response({"detail": ("Feil brukernavn eller passord")}, status=401)


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
        except Token.DoesNotExist:
            Token.objects.create(user=user)
            return Response({"detail": ("New TIHLDE member added")}, status=200)
    else:
        return Response({"detail": ("Incorrect user_id")}, status=400)
