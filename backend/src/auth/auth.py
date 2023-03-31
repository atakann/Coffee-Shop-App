import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH_DOMAIN = ""
ALGORITHMS = ["RS256"]
API_AUDIENCE = "dev"

class AuthError(Exception):
    """
    A standardized way to communicate auth failure modes
    """
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
    raise Exception("Not Implemented")

def check_permissions(permission, payload):
    raise Exception("Not Implemented")

def verify_decode_jwt(token):
    raise Exception("Not Implemented")

def requires_auth(permission=""):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        
        return wrapper
    return requires_auth_decorator
