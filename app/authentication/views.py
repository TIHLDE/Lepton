from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from django.core.handlers.asgi import ASGIRequest
from django.http import JsonResponse, QueryDict

from sentry_sdk import capture_exception

from app.authentication.exceptions import APIAuthUserDoesNotExist
from app.authentication.serializers import (
    AuthSerializer,
    OAuthClientIdSerializer,
    OAuthNewCodeSerializer,
)
from app.authentication.models import OAuthApps, OAuthRequest
from app.authentication.utils import generate_otp, add_query_params
from app.common.permissions import set_user_id
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


@api_view(["GET"])
def get_oauth_app(request):
    # type: (Request) -> Response

    # Validate request params
    serializer = OAuthClientIdSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(
            {"detail": "Du mangler nødvendig informasjon for å hente OAuth appen"},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )

    # Get Request params
    client_id = serializer.data["client_id"]

    # Check if app exists
    auth_app = OAuthApps.objects.get(client_id=client_id)
    if not auth_app:
        return Response(
            {"detail": f"OAuth appen med klient id '{client_id}' eksisterer ikke"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Return the app info
    return Response(
        {
            "client_id": auth_app.client_id,
            "app_name": auth_app.app_name,
            "app_image": auth_app.image,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def temporary_oauth_code(request):
    # type: (Request) -> Response

    # Check authentication
    set_user_id(request)
    if not request.user:
        return Response(
            {"detail": "Du må være logget inn for å lage en ny OAuth kode"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    print("\n\n\n")
    print(request.query_params)

    # Validate request params
    serializer = OAuthNewCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"detail": "Du mangler nødvendig informasjon for å lage en ny OAuth kode"},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )

    print(request.user)

    # Get Request params
    client_id = serializer.data["client_id"]
    redirect_uri = serializer.data["redirect_uri"]

    # Check if client_id exists and
    auth_app = OAuthApps.objects.get(client_id=client_id)
    if not auth_app:
        return Response(
            {"detail": f"OAuth appen med klient id '{client_id}' eksisterer ikke"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Generate one-time-code
    existing_codes = [p.auth_code for p in OAuthRequest.objects.all()]
    code = generate_otp()
    while code in existing_codes:
        code = generate_otp()

    expires = now() + timedelta(minutes=5)
    print("OAuth Code expires at: ", expires)
    token = request.META.get("HTTP_X_CSRF_TOKEN")

    # Save it to the database
    OAuthRequest.objects.create(
        client_id=auth_app,
        auth_code=code,
        user_token=token,
        expires=expires,
    )

    # Create the redirect url
    code_url = add_query_params(redirect_uri, {"code": code})

    # Redirect the user to the redirect_uri with the code
    return Response({"redirect_url": code_url, "code": code}, status=status.HTTP_200_OK)


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def oauth_access_token(request):
    # type: (ASGIRequest) -> Response

    if request.method != "POST":
        return Response(
            {"detail": "Du må sende en POST request for å få en access token"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    data = QueryDict(request.body.decode("utf-8"))

    code = data.get("code")
    grant_type = data.get("grant_type")

    # TODO: this should probably be hashed with an algorithm
    client_secret = data.get("client_secret")

    if code == None:
        return JsonResponse(
            data={"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    print("Code: ", code)
    print("Grant type: ", grant_type)
    print("Client secret: ", client_secret)

    oauth_request = OAuthRequest.objects.get(auth_code=code)
    print("OAuth request: ", oauth_request)

    if oauth_request == None:
        return JsonResponse(
            data={"error": f"No OAuth request with code '{code}'"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if oauth_request.expires < now():
        oauth_request.delete()
        return JsonResponse(
            data={"error": f"OAuth code '{code}' has expired"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if oauth_request.client_id.client_secret != client_secret:
        # Delete the request if the client secret does not match
        # Prevents brute force attacks
        oauth_request.delete()
        return JsonResponse(
            data={"error": "Client secret does not match"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return JsonResponse(
        data={"access_token": oauth_request.user_token, "token_type": "bearer"},
        status=status.HTTP_200_OK,
    )
