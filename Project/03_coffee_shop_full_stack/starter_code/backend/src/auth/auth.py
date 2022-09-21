import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-efynh0m7.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee-shop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code



# Verify
def verify_decode_jwt(token):
    #Get Data In Header
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # Get data in header
    unverified_header = jwt.get_unverified_header(token)

    # Choose key
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description':'Authorization malformed'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid':key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    # Final verification
    if rsa_key:
        try:
            # use key to validate
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please check the audience and issure'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropraite key'
    },400)


## Auth Header
def get_token_auth_header():
    if 'Authorization' not in request.headers:
         raise AuthError({
                'code': 'invalid_claims',
                'description': 'No header found'
            }, 401)
 
    auth_header = request.headers['Authorization']
    auth_path = auth_header.split(' ')

    if len(auth_path) != 2:
         raise AuthError({
                'code': 'invalid_claims',
                'description': 'Wrong Claims'
            }, 401)
    
    if auth_path[0].lower() != 'bearer':
        raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect jwt'
            }, 401)
    
    return(auth_path[1])


# Check Permission
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claim',
            'description': 'Permission not included in jwt'
        },400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'Unauthorize',
            'description':'permission not found'
        }, 403)
    
    return True



# Require Auth Decorator method
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