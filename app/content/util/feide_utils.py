import jwt
import requests
import secrets
import string

from requests.auth import HTTPBasicAuth
from datetime import datetime

from settings import (
    FEIDE_CLIENT_ID,
    FEIDE_CLIENT_SECRET,
    FEIDE_REDIRECT_URL,
    FEIDE_TOKEN_URL,
    FEIDE_USER_GROUPS_INFO_URL,
    FEIDE_USER_INFO_URL
)

from app.content.mixins import (
    FeideTokenNotFoundError,
    FeideGetTokenError,
    FeideUserInfoNotFoundError,
    FeideUsernameNotFoundError,
    FeideGetUserInfoError,
    FeideUserGroupsNotFoundError,
    FeideParseGroupsError,
    FeideGetUserGroupsError
)


def get_feide_tokens(code: str) -> tuple[str, str]:
    """Get access and JWT tokens for signed in Feide user"""

    try:
        grant_type = "authorization_code"

        auth = HTTPBasicAuth(
            username=FEIDE_CLIENT_ID,
            password=FEIDE_CLIENT_SECRET
        )

        payload = {
            "grant_type": grant_type,
            "client_id": FEIDE_CLIENT_ID,
            "redirect_uri": FEIDE_REDIRECT_URL,
            "code": code
        }

        response = requests.post(
            url=FEIDE_TOKEN_URL,
            auth=auth,
            data=payload
        )

        json = response.json()

        if (
            not "access_token" in json or
            not "id_token" in json
        ):
            raise FeideTokenNotFoundError()

        return (json["access_token"], json["id_token"])
    except Exception:
        raise FeideGetTokenError


def get_feide_user_info_from_jwt(jwt_token: str) -> tuple[str, str]:
    """Get Feide user info from jwt token"""
    user_info = jwt.decode(jwt_token, options={"verify_signature": False})

    if (
        not "name" in user_info or
        not "https://n.feide.no/claims/userid_sec" in user_info
    ):
        raise FeideUserInfoNotFoundError
    
    feide_username = None
    for id in user_info["https://n.feide.no/claims/userid_sec"]:
        if "feide:" in id:
            feide_username = id.split(":")[1].split("@")[0]
    
    if not feide_username:
        raise FeideUsernameNotFoundError
        
    return (
        user_info["name"],
        feide_username
    )

def get_feide_user_info(access_token: str):
    """Get Feide user info from request"""

    try:
        response = requests.get(
            url=FEIDE_USER_INFO_URL,
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        user_info = response.json()

        if (
            not "name" in user_info or
            not "https://n.feide.no/claims/userid_sec" in user_info
        ):
            raise FeideUserInfoNotFoundError
        
        feide_username = None
        for id in user_info["https://n.feide.no/claims/userid_sec"]:
            if "feide:" in id:
                feide_username = id.split(":")[1].split("@")[0]
        
        if not feide_username:
            raise FeideUsernameNotFoundError
            
        return (
            user_info["name"],
            feide_username
        )
    except Exception:
        raise FeideGetUserInfoError


def get_feide_user_groups(access_token: str) -> list[str]:
    """Get a Feide user's groups"""

    try:
        response = requests.get(
            url=FEIDE_USER_GROUPS_INFO_URL,
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )

        groups = response.json()

        if not groups:
            raise FeideUserGroupsNotFoundError

        return [
            group["id"] # Eks: fc:fs:fs:prg:ntnu.no:ITBAITBEDR
            for group
            in groups
        ]
    except Exception:
        raise FeideGetUserGroupsError


def parse_feide_groups(groups: list[str]) -> list[str]:
    """Parse groups and return list of group slugs"""
    program_codes = [
        "BIDATA",
        "ITBAITBEDR",
        "BDIGSEC",
        "ITMAIKTSA",
        "ITBAINFODR",
        "ITBAINFO"
    ]
    program_slugs = [
        "dataingenir",
        "digital-forretningsutvikling",
        "digital-infrastruktur-og-cybersikkerhet",
        "digital-samhandling",
        "drift-studie",
        "informasjonsbehandling"
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
        raise FeideParseGroupsError

    return slugs


def generate_random_password(length=12):
    """Generate random password with ascii letters, digits and punctuation"""
    characters = string.ascii_letters + string.digits + string.punctuation

    password = ''.join(secrets.choice(characters) for i in range(length))
    
    return password

def get_study_year() -> str:
    today = datetime.today()
    current_year = today.year
    
    # Check if today's date is before July 20th
    if today < datetime(current_year, 7, 20):
        current_year -= 1
    
    return str(current_year)