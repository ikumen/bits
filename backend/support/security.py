import logging

from flask import session, request, redirect
from functools import wraps
from werkzeug.exceptions import Unauthorized
from backend import support
from backend.support.github import github


def authorized(f):
    """Decorator for methods that require an authorized user, unauthorized 
    users will get redirected to /signout."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get(support.AUTHORIZED_SESSION_KEY) is None:
            if request.content_type == 'application/json':
                raise Unauthorized('Authorization is required for this action!')
            else:
                return redirect('/signout')        
        return f(*args, **kwargs)
    return decorated

# export it
authorized_handler = github.authorized_handler
authorize = github.authorize

def get_user(access_token):
    return github.get('/user', access_token=access_token)