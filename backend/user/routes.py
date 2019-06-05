import logging

from flask import current_app, session, jsonify
from . import repository, bp
from backend import support


log = logging.getLogger(__name__)


@bp.route('/user')
def get_user():
    user = repository.get_for_public(current_app.config.get('GITHUB_USER_ID'))
    if session.get(support.AUTHORIZED_SESSION_KEY) and user:
        user['authenticated'] = True
    return jsonify(user)
