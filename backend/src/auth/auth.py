import json
from functools import wraps
from urllib.request import urlopen

from flask import request
from jose import jwt, JWTError

AUTH0_DOMAIN = 'sw-ark.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee-shop-api-id'
CLIENT_ID = 'AXZyXNVKFfJ4ak6Tgs1buK0ZHuafGf7H'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    auth_header = request.headers.get('Authorization', None)
    if auth_header:
        if 'Bearer ' not in auth_header:
            raise AuthError({
                'code': 'malformed_header',
                'description': 'Malformed authorization token.'
            }, 400)
        auth_header = auth_header.split(' ')[1]
        return auth_header
    raise AuthError({
        'code': 'no_token_header',
        'description': 'No authorization token provided '
    }, 400)


def check_permissions(permission, payload):
    if permission in payload['permissions']:
        return True
    raise AuthError({
        'code': 'unauthorized_action',
        'description': 'Action is not authorized'
    }, 401)


def get_jwks():
    return urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json').read()


def verify_decode_jwt(token):
    try:
        unverified_headers = jwt.get_unverified_header(token)
    except JWTError:
        raise AuthError({
            'code': 'invalid_token',
            'description': 'Incorrect token provided.'
        }, 400)

    kid = unverified_headers['kid']
    jwks = json.loads(get_jwks())
    rsa_key = {}
    for k in jwks['keys']:
        if k['kid'] == kid:
            rsa_key = {
                'kty': k['kty'],
                'kid': k['kid'],
                'use': k['use'],
                'n': k['n'],
                'e': k['e']
            }
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                json.dumps(rsa_key),
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
