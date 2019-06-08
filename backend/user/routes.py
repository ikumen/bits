import logging

from flask import current_app, session, jsonify
from backend import support
from . import model as User, bp


log = logging.getLogger(__name__)


@bp.route('/user')
def get_user():
    auth_user = User.get_for_public(current_app.config.get('GITHUB_USER_ID'))
    if session.get(support.AUTHORIZED_SESSION_KEY) and auth_user:
        auth_user['authenticated'] = True
    return jsonify(auth_user)
