import logging
import json

from flask import Flask, g, Blueprint, current_app, redirect, request, session
from functools import wraps
from google.auth import credentials

AUTHORIZED_SESSION_KEY = 'IS_AUTHORIZED'

def strftime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

def authorized(f):
    """Decorator for methods that require an authorized user, unauthorized 
    users will get redirected to /signout."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get(AUTHORIZED_SESSION_KEY) is None:
            if request.content_type == 'application/json':
                raise AuthenticationError('Authorization is required for this action!')
            else:
                return redirect('/signout')        
        return f(*args, **kwargs)
    return decorated


def handle_error(error):
    """Return errors into appropriate Flask response"""
    print(error)
    return make_response(error.to_dict(), status_code=error.status_code)


def make_response(payload=None, status_code=200, mimetype='application/json', serialize=True):
    """Helper for making Flask response."""
    if payload is None:
        status_code = 204
    elif serialize:
        payload = json.dumps(payload)

    return current_app.response_class(
        response=payload,
        status=status_code,
        mimetype=mimetype)

class AppError(Exception):
    status_code = 500

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return dict(message=self.message)

class BitNotFoundError(AppError):
    status_code = 404

    def __init__(self, id):
        super(BitNotFoundError, self).__init__("Bit '%s' not found!" % id)

class AuthenticationError(AppError):
    status_code = 403

class EmulatorCredentials(credentials.Credentials):
    def __init__(self):
        self.token = b'seekrit'
        self.expiry = None

    @property
    def valid(self): 
        return True

    def refresh(self, unused_request):
        raise RuntimeError('Should never be refreshed.')

