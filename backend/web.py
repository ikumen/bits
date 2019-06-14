import json
import logging
import requests

from concurrent import futures
from flask import Blueprint, current_app, redirect, render_template, session
from werkzeug.exceptions import Unauthorized, Forbidden
from backend.support import security
from backend.user import model as User
from backend import support


log = logging.getLogger(__name__)
bp = Blueprint('webapp', __name__)


@bp.route('/bits/<id>')
@bp.route('/bits')
@bp.route('/about')
@bp.route('/errors/<id>')
@bp.route('/errors')
@bp.route('/')
def frontend(id=None):
    """Routes handled by the frontend SPA."""
    return render_template('index.html')

@bp.route('/bits/<id>/edit')
@bp.route('/settings')
def secured_frontent(id=None):
    if session.get(support.AUTHORIZED_SESSION_KEY) is None:
        return redirect('/errors/401')
    return render_template('index.html')

@bp.route('/signin')
def signin():
    """Start signin flow if no authorized user found, 
    otherwiseredirect to home page.
    """
    if session.get(support.AUTHORIZED_SESSION_KEY):
        return redirect('/')
    return security.authorize()

@bp.route('/signout')
def signout():
    session.clear()
    return redirect('/')

@bp.route('/signin/complete')
@security.authorized_handler
def signin_complete(access_token):
    """Complete the signin process"""
    if access_token is None:
        raise Unauthorized('Authorization with provider failed!')

    # get info for the user that just authenticated
    user_info = security.get_user(access_token)

    # Authorization successful, but verify it's us. 
    # Note: GitHub will send our id in OAuth response as login
    if 'login' not in user_info or \
            user_info['login'] != current_app.config.get('GITHUB_USER_ID'):
        raise Forbidden('Sorry you are not an authorized user!')

    # update with latest user info
    User.update(access_token=access_token, **user_info)

    # flag this session as belonging to us
    session[support.AUTHORIZED_SESSION_KEY] = True

    return redirect('/')
