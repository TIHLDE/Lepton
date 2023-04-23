import os
import json
from app.constants import AUTH0_AUDIENCE, AUTH0_DOMAIN
from app.content.models.user import User
import jwt
import requests
from django.contrib.auth import authenticate


def get_jwt_from_request(request):    
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token

def decode_jwt(token):
    header = jwt.get_unverified_header(token)
    jwks = requests.get('https://{}/.well-known/jwks.json'.format(AUTH0_DOMAIN)).json()

    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found while decoding token.')

    return jwt.decode(token, public_key, audience=AUTH0_AUDIENCE, issuer='https://{}/'.format(AUTH0_DOMAIN), algorithms=['RS256'])

def get_userid_from_decoded_jwt(payload):
    user_id = payload.get('sub').replace('|', '.')
    authenticate(remote_user=user_id)

    return user_id

def get_user_from_request(request):
    user_id = get_userid_from_decoded_jwt(decode_jwt(get_jwt_from_request(request)))

    return User.objects.get(user_id=user_id)