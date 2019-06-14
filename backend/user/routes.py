import logging

from flask import current_app, session, jsonify
from backend import support
from backend.support import security
from . import model as User, bp
from backend.bit import model as Bit
from backend.sync import sync_service


log = logging.getLogger(__name__)


@bp.route('/user/stats')
@security.authorized
def stats():
    bits = Bit.all(projection=['id', 'published_at'])
    syncs = sync_service.all()
    return support.make_response(payload=dict(bits=bits, syncs=syncs))

@bp.route('/user')
def user():
    auth_user = User.get_for_public(current_app.config.get('GITHUB_USER_ID'))
    if session.get(support.AUTHORIZED_SESSION_KEY) and auth_user:
        auth_user['authenticated'] = True
    return jsonify(auth_user)
