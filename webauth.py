"""This module contains wrappers for the WebAuth API
and a rest_framework authentication class for integration
with django.

The session data is expected to be on the form:
{
    'memberof_group': [
        'list',
    ],
    'cn': [
        'Full Name'
    ],
    'homedirectory': [
        '/path/to/home/directory'
    ],
    'uid': [
        'username'
    ],
    'mail': [
        'list.of@emails'
    ],
    'givenname': [
        'Firstname'
    ],
    'sn': [
        'Lastname'
    ]
}
"""

from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings

from functools import wraps
import secrets
from logzero import logger
import requests

AUTH = settings.WEB_AUTH
API_URL = AUTH['api_url']
TOKEN_HEADER = AUTH['token_header']
DJANGO_TOKEN_HEADER = AUTH['django_token_header']

def verify(token):
    """Uses the verify endpoint of the WebAuth API to verify the
    authenticity of the token.

    :param token: the WebAuth token
    :type token: str or bytes
    :returns: the session data, or None
    :see: this modules docstring for description of the session data
    """
    try:
        r = requests.get(API_URL + 'verify', headers={TOKEN_HEADER: token})
        if not r.status_code == requests.codes.ok:
            return None
        return r.json()
    except requests.exceptions.ConnectionError as e:
        logger.error('Unable to connect to the WebAuth API: "{}"'.format(API_URL))
        raise exceptions.AuthenticationFailed('Unable to connect to the WebAuth API')
        raise e

class Authentication(authentication.BaseAuthentication):
    """
    Used to authenticate the user using the WebAuth tokens.
    """
    def authenticate(self, request):
        """The WebAuth token is stored in the `X-CSRF-Token` header.
        Use the WebAuth API to verify the authenticity of the token,
        and set the data.

        If the WebAuth token is valid, but there does not exist an entry
        for the user in the django Users model, then an entry with its
        username will be created (with a randomly generated password).
        The created user will only store the username.

        From: http://www.django-rest-framework.org/api-guide/authentication/#example
        """
        token = request.META.get(DJANGO_TOKEN_HEADER, None)
        if not token:
            return None

        session = verify(token)
        if not session:
            raise exceptions.AuthenticationFailed('Invalid WebAuth token')

        try:
            username = session['uid']
            if type(username) == list:
                username = username[0]

            user, created = User.objects.get_or_create(username=username)
            if created:
                # Set the password to a string of 64 random bytes, as
                # it is not to be accessed directly anyway.
                user.password = secrets.token_bytes(64)
                user.save()
                logger.debug('Created local user "{}"'.format(username))
            logger.debug('Authenticated user "{}" using WebAuth token'.format(username))
        except ValueError:
            raise exceptions.AuthenticationFailed('Not a valid username')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
