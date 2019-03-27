import json
import logging
import requests

from concurrent import futures
from flask import Blueprint, current_app, redirect, render_template, session
from . import github, Users
from . import helpers


log = logging.getLogger(__name__)
bp = Blueprint('webapp', __name__)


@bp.route('/bits/<id>')
@bp.route('/bits/<id>/edit')
@bp.route('/bits')
@bp.route('/about')
@bp.route('/errors/<id>')
@bp.route('/errors')
@bp.route('/settings')
@bp.route('/')
def app(id=None):
    return render_template('index.html')


@bp.route('/signin')
def signin():
    """Start signin flow if no authorized user found, 
    otherwiseredirect to home page.
    """
    if session.get(helpers.AUTHORIZED_SESSION_KEY):
        return redirect('/')
    return github.authorize(scope='read:user,gist')


@bp.route('/signout')
def signout():
    session.clear()
    return redirect('/')


@bp.route('/signin/complete')
@github.authorized_handler
def signin_complete(access_token):
    """Complete the signin process"""
    if access_token is None:
        raise helpers.AuthenticationError(message='Authorization failed!')

    # get info for the user that just authenticated
    user_info = github.get('/user', access_token=access_token)

    # Authorization successful, but verify it's us. 
    # Note: GitHub will send our id in OAuth response as login
    if 'login' not in user_info or \
            user_info['login'] != current_app.config.get('GITHUB_USER_ID'):
        raise helpers.AuthenticationError(message='Sorry you are not an authorized user!')

    # update with latest user info
    Users.upsert(access_token=access_token, **user_info)

    # flag this session as belonging to us
    session[helpers.AUTHORIZED_SESSION_KEY] = True

    return redirect('/')
