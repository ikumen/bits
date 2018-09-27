import logging

from flask import session, jsonify, redirect
from functools import wraps
from services import github, UserService
from helpers import handle_error


log = logging.getLogger(__name__)

USER_SESS_ATTR = 'user'
OAUTH_ATTR_NAME = 'oauth'

@github.access_token_getter
def token_getter():
    return session.get(OAUTH_ATTR_NAME)


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
        user = current_user()
        if not user:
            log.debug('User is not authenticated, starting authentication!')
            return github.authorize(scope='read:user,gist')
        return f(user, **kwargs)
    return decorated


def post_authorization(f):
    """Decorator for method that handles authorization."""
    @wraps(f)
    def decorated(oauth_token, **kwargs):
        if not oauth_token:
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
        user = UserService.update(
            id=user_info['login'], 
            name=user_info['name'],
            avatar_url=user_info['avatar_url'],
            oauth=oauth_token,
            upsert=True)

        # put user back in session
        # NOTE: oauth is removed from user before serialized into session
        # see User.to_json for details. Use session[OAUTH_ATTR_NAME] for
        # authenticated user's oauth token
        session[USER_SESS_ATTR] = user
        session[OAUTH_ATTR_NAME] = user.oauth
        return f(user, **kwargs)
    return decorated


def current_user():
    return session.get(USER_SESS_ATTR)


