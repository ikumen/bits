import logging

from flask import session, jsonify, redirect
from functools import wraps
from services import github, user_service
from helpers import handle_error


log = logging.getLogger(__name__)

USER_SESS_ATTR = 'user'
OAUTH_ATTR_NAME = 'oauth'

@github.access_token_getter
def token_getter():
    oauth_token = session.get(OAUTH_ATTR_NAME)
    if oauth_token is None:
        oauth_token = session.get(USER_SESS_ATTR, {}).get(OAUTH_ATTR_NAME)
    return oauth_token


def authorized(f):
    """Decorator for methods that require an authorized user. Decorated
    route handler will get user passed in.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user = current_user()
        if not user:
            return redirect('/signout')
        else:
            return f(user, **kwargs)
    return decorated


def authorization_start(f):
    """Decorator for method that starts authorization."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user() is None:
            log.debug('User is not authenticated, starting authentication!')
            return github.authorize(scope='read:user,gist')
        return f(*args, **kwargs)
    return decorated


def post_authorization(f):
    """Decorator for method that handles authorization."""
    @wraps(f)
    def decorated(oauth_token, **kwargs):
        if oauth_token is None:
            return handle_error(message='Authorization failed!', status=401)

        # temporarily save access token
        session[OAUTH_ATTR_NAME] = oauth_token

        # let's get user login info
        user_info = github.get('/user')
        if 'login' not in user_info:
            return handle_error(message='Unable to load user!', status=401)

        # remove temporary token
        session.pop(OAUTH_ATTR_NAME)
        # persists/update user associated with this token

        user = user_service.get(user_info['login'])
        if user is None:
            user = {
                '_id': user_info['login'], 
                'name': user_info['name'],
                'avatar_url': user_info['avatar_url'],
                'oauth': oauth_token
            }
            user_service.save(user)
        else:           
            user.update({
                'name': user_info['name'],
                'avatar_url': user_info['avatar_url'],
                'oauth': oauth_token
            })
            user_service.update(user['_id'], **user)

        session[USER_SESS_ATTR] = user
        return f(user, **kwargs)
    return decorated


def current_user():
    return session.get(USER_SESS_ATTR)


