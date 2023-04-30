import time

import requests

from app.constants import AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN
    

def get_user_information(user_id):
    """
    Gets zipped study programs + start years, name and Feide username from Auth0 given the user_id.

    Example: "olanord", "Ola Nordmann", "olanord@stud.ntnu.no", [('BIDATA', '2020')].
    """
    token_manager = ManagementTokenManager()

    response = requests.get(
        f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}",
        headers={"Authorization": f"Bearer {token_manager.get_token()}"},
    ).json()

    feide_username = response["nickname"]
    name = response["name"]
    email = response["email"]

    # Example format: ['fc:fs:fs:kull:ntnu.no:BIDATA:2020H']
    metadata = response["app_metadata"]["programs"]

    programs = [p.split(":")[5] for p in metadata]
    years = [p.split(":")[6][:4] for p in metadata]

    return feide_username, name, email, zip(programs, years)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ManagementTokenManager(metaclass=Singleton):
    """
    Singleton class for getting and refreshing Auth0 Management API tokens.
    """

    def __init__(self):
        self.token, self.duration = self._get_management_token()
        self.timestamp = time.time()

    def _get_management_token(self):
        response = requests.post(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": AUTH0_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "audience": f"https://{AUTH0_DOMAIN}/api/v2/",
            },
        ).json()

        return response["access_token"], response["expires_in"]

    def get_token(self):
        # Refresh token if expired, then return token.
        if time.time() > self.timestamp + self.duration:
            self.__init__()

        return self.token
