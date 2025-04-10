from functools import wraps

from rest_framework import status
from rest_framework.response import Response

from app.apikey.util.valid import is_valid_uuid


def check_api_key(view):
    """Decorator to check if the request has a valid API key."""

    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        from app.apikey.models.key import ApiKey

        api_key = request.headers.get("x-api-key")
        if not api_key:
            return Response(
                {"detail": "API nøkkel mangler"},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_valid_api_key = is_valid_uuid(api_key)
        if not is_valid_api_key:
            return Response(
                {"detail": "API nøkkel er ikke riktig format. Den må være UUID"},
                status=status.HTTP_403_FORBIDDEN,
            )

        valid_api_key = ApiKey.objects.filter(key=api_key).first()

        if not valid_api_key:
            return Response(
                {"detail": "Ugyldig API nøkkel"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return view(request, *args, **kwargs)

    return _wrapped_view
