from flask import request
from werkzeug.exceptions import Unauthorized, Forbidden

from ..config import api_key as registred_api_key

def auth_required(func):
    #func = api.doc(security='apikey')(func)
    def check_auth(*args, **kwargs):
        if 'X-API-KEY' not in request.headers:
            raise Unauthorized('No API Key provided')
        key = request.headers['X-API-KEY']

        if key != registred_api_key or not registred_api_key:
            raise Forbidden('Wrong API Key')

        return func(*args, **kwargs)
    return check_auth