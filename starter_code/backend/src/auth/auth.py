import json
from flask import request, _request_ctx_stack,abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-i20z2y54qtc46c2h.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffeeshop'

## AuthError Exception - AuthError Exception-A standardized way to communicate auth failure modes

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header
# Get the header from the request
# Raise an AuthError if no header is present
# Attempt to split bearer and the token
# Raise an AuthError if the header is malformed
# return the token part of the header

def get_token_auth_header():
   auth=request.headers.get('Authorization',None)
   if not auth:
     raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)
   
   parts=auth.split()
   if parts[0].lower() != 'bearer':
       raise AuthError({
           'code':'invalid_header',
           'description': 'Authorization header must start with "Bearer".'
       },401)
   elif len(parts) ==1:
       raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)
   elif len(parts) >2 :
       raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
   
   token=parts[1]
   return token
       
# Check Permissions
# Inputs - permission: string permission (i.e. 'post:drink') , payload: decoded jwt payload
# Raise an AuthError if permissions are not included in the payload
    # Raise an AuthError if the requested permission string is not in the payload permissions array
    # return true otherwise

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
                            'code': 'invalid_claims',
                            'description': 'Permissions not included in JWT.'
                        }, 400)
    
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True

# Decode JWT
# Should be an Auth0 token with key id (kid)
# Should verify the token using Auth0 /.well-known/jwks.json
# Should decode the payload from the token
# Should validate the claims
# return the decoded payload

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
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

# Implement @requires_auth(permission) decorator method
# @INPUTS permission: string permission (i.e. 'post:drink')
# Use the get_token_auth_header method to get the token
# Use the verify_decode_jwt method to decode the jwt
# Use the check_permissions method validate claims and check the requested permission
# Return the decorator which passes the decoded payload to the decorated method

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            # print(token)
           
            payload = verify_decode_jwt(token)
            # print(payload)
            
            result=check_permissions(permission, payload)
            # print(result)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator