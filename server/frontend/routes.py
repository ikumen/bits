import logging

from flask import request, redirect, session, Blueprint, render_template
from .. import security
from ..services import github


bp = Blueprint('/', __name__, 
    static_folder="/Volumes/Data/Projects/python-apps/bits/dist/static",
    static_url_path="/static")
log = logging.getLogger(__name__)


@bp.route('/', methods=['get'])
@bp.route('/about', methods=['get'])
@bp.route('/@<user_id>', methods=['get'])
@bp.route('/@<user_id>/bits/<bit_id>', methods=['get'])
def home(user_id=None, bit_id=None):
    return render_template('index.html')    


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
    return redirect('/@' + user['_id'])
