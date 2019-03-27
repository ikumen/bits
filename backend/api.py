import logging

from flask import jsonify, Blueprint, current_app, request, session
from . import helpers
from . import Users, Bits


bp = Blueprint('api', __name__, url_prefix='/api')
log = logging.getLogger(__name__)


@bp.route('/user')
def get_user():
    user = Users.get_for_public(current_app.config.get('GITHUB_USER_ID'))
    if session.get(helpers.AUTHORIZED_SESSION_KEY) and user:
        user['authenticated'] = True
    return jsonify(user)

@bp.route('/bits', methods=['get'])
def list_bits():
    return jsonify(Bits.all_by_created_at())

@bp.route('/bits/<id>', methods=['get'])
def get_bit(id):
    log.info('id=%s' % id)
    bit = Bits.get(id)
    if bit is None:
        raise helpers.BitNotFoundError(id)
    return jsonify(bit)

@bp.route('/bits/<id>', methods=['post', 'patch'])
@helpers.authorized
def save_bit(id=None):
    bit_data = request.get_json()
    if not id or id == 'new':
        return helpers.make_response(Bits.create(**bit_data), status_code=201)
    return helpers.make_response(Bits.save(id=id, **bit_data), status_code=200)

@bp.route('/bits/<id>', methods=['delete'])
@helpers.authorized
def delete_bit(id):
    Bits.delete(id)
    return helpers.make_response()

@bp.route('/settings/reload', methods=['get'])
@helpers.authorized
def reload_bits():
    Bits.load()
    return 'ok'

# @bp.route('/settings', methods=['get'])
# @helpers.authorized
# def settings():
#     return helpers.make_response(Bits.settings())




