import logging

from flask import request, redirect, session, Blueprint, render_template
from .. import security
from ..services import github


bp = Blueprint('/', __name__)
log = logging.getLogger(__name__)


@bp.route('/')
def home():
    return 'home'    

@bp.route('/@<user_id>')
@security.authorized
def user(user, user_id):
    print(user)
    print(user_id)
    return 'hello'


@bp.route('/signin')
@security.authorization_start
def signin():
    log.debug('Found authenticated user, redirect to home!')
    user = security.current_user()
    return redirect('/@' + user['_id'])


@bp.route('/signout', methods=['get'])
def signout():
   log.debug('Signing out!')
   session.clear()
   return redirect('/')


@bp.route('/signin/complete')
@github.authorized_handler
@security.post_authorization
def authorized(user):
    return redirect('/user')
