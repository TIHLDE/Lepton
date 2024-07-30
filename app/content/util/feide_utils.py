import jwt
import requests
import secrets
import string

from requests.auth import HTTPBasicAuth
from datetime import datetime

from app.settings import (
    FEIDE_CLIENT_ID,
    FEIDE_CLIENT_SECRET,
    FEIDE_REDIRECT_URL,
    FEIDE_TOKEN_URL,
    FEIDE_USER_GROUPS_INFO_URL,
)

from app.content.exceptions import (
    FeideTokenNotFoundError,
    FeideGetTokenError,
    FeideUserInfoNotFoundError,
    FeideUsernameNotFoundError,
    FeideUserGroupsNotFoundError,
    FeideParseGroupsError,
    FeideGetUserGroupsError,
    FeideUsedUserCode,
)


def get_feide_tokens(code: str) -> tuple[str, str]:
    """Get access and JWT tokens for signed in Feide user"""

    grant_type = "authorization_code"

    auth = HTTPBasicAuth(username=FEIDE_CLIENT_ID, password=FEIDE_CLIENT_SECRET)

    payload = {
        "grant_type": grant_type,
        "client_id": FEIDE_CLIENT_ID,
        "redirect_uri": FEIDE_REDIRECT_URL,
        "code": code,
    }

    response = requests.post(url=FEIDE_TOKEN_URL, auth=auth, data=payload)

    if response.status_code == 400:
        raise FeideUsedUserCode()

    if response.status_code != 200:
        raise FeideGetTokenError()

    json = response.json()

    if "access_token" not in json or "id_token" not in json:
        raise FeideTokenNotFoundError()

    return (json["access_token"], json["id_token"])


def get_feide_user_info_from_jwt(jwt_token: str) -> tuple[str, str]:
    """Get Feide user info from jwt token"""
    user_info = jwt.decode(jwt_token, options={"verify_signature": False})

    if (
        "name" not in user_info
        or "https://n.feide.no/claims/userid_sec" not in user_info
    ):
        raise FeideUserInfoNotFoundError()

    feide_username = None
    for id in user_info["https://n.feide.no/claims/userid_sec"]:
        if "feide:" in id:
            feide_username = id.split(":")[1].split("@")[0]

    if not feide_username:
        raise FeideUsernameNotFoundError()

    return (user_info["name"], feide_username)


def get_feide_user_groups(access_token: str) -> list[str]:
    """Get a Feide user's groups"""

    response = requests.get(
        url=FEIDE_USER_GROUPS_INFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code != 200:
        raise FeideGetUserGroupsError()

    groups = response.json()

    if not groups:
        raise FeideUserGroupsNotFoundError()

    return [group["id"] for group in groups]  # Eks: fc:fs:fs:prg:ntnu.no:ITBAITBEDR


def parse_feide_groups(groups: list[str]) -> list[str]:
    """Parse groups and return list of group slugs"""
    program_codes = [
        "BIDATA",
        "ITBAITBEDR",
        "BDIGSEC",
        "ITMAIKTSA",
        "ITBAINFODR",
        "ITBAINFO",
    ]
    program_slugs = [
        "dataingenir",
        "digital-forretningsutvikling",
        "digital-infrastruktur-og-cybersikkerhet",
        "digital-samhandling",
        "drift-studie",
        "informasjonsbehandling",
    ]

    slugs = []

    for group in groups:

        id_parts = group.split(":")

        group_code = id_parts[5]

        if group_code not in program_codes:
            continue

        index = program_codes.index(group_code)
        slugs.append(program_slugs[index])

    if not len(slugs):
        raise FeideParseGroupsError()

    return slugs


def generate_random_password(length=12):
    """Generate random password with ascii letters, digits and punctuation"""
    characters = string.ascii_letters + string.digits + string.punctuation

    password = "".join(secrets.choice(characters) for _ in range(length))

    return password


def get_study_year() -> str:
    today = datetime.today()
    current_year = today.year

    # Check if today's date is before July 20th
    if today < datetime(current_year, 7, 20):
        current_year -= 1

    return str(current_year)
