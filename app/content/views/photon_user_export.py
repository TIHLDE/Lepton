from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.common.permissions import is_admin_user, set_user_id
from app.content.models import User


@api_view(["GET"])
def photon_user_export(request):
    """
    Read-only bulk export of every user, for the one-time migration to Photon
    (the new backend). Photon has no access to this database, so it consumes
    this endpoint instead of a direct SQL connection.

    Returns only the fields Photon's user import needs. Password hashes and auth
    tokens are deliberately left out: Photon sets its own placeholder password
    and users authenticate via Feide afterwards, so no secret ever leaves here.

    Locked to superusers who are also in HS/Index. This exposes every member's
    name, email and bio in one response, so it should be removed once the
    migration is done.

    Header: X-Csrf-Token — the caller's auth token.
    """
    set_user_id(request)

    if request.user is None:
        return Response(
            {"detail": "Manglende autentiseringsinformasjon."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not (is_admin_user(request) and request.user.is_superuser):
        return Response(
            {"detail": "Krever superbruker i HS/Index."},
            status=status.HTTP_403_FORBIDDEN,
        )

    users = (
        User.objects.select_related("bio")
        .order_by("created_at")
        .values(
            "user_id",
            "first_name",
            "last_name",
            "email",
            "gender",
            "allergy",
            "image",
            "is_superuser",
            "is_active",
            "allows_photo_by_default",
            "accepts_event_rules",
            "created_at",
            "updated_at",
            "bio__description",
            "bio__gitHub_link",
            "bio__linkedIn_link",
        )
    )

    # Flatten the bio__ prefixes into the field names Photon expects.
    payload = [
        {
            **{k: v for k, v in u.items() if not k.startswith("bio__")},
            "description": u["bio__description"],
            "gitHub_link": u["bio__gitHub_link"],
            "linkedIn_link": u["bio__linkedIn_link"],
        }
        for u in users
    ]

    return Response({"count": len(payload), "users": payload})
