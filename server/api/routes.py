import logging

from bson import json_util
from flask import Blueprint, request, jsonify
from ..helpers import handle_error
from ..security import authorized, current_user
from ..services import bit_service


bp = Blueprint('/api', __name__)
log = logging.getLogger(__name__)


@bp.route('/@<user_id>/bits', methods=['get'])
def api_list_bits(user_id):
    bits = bit_service.list(filters={'user_id': user_id})
    return json_util.dumps(bits)


@bp.route('/@<user_id>/bits', methods=['put', 'post'])
@authorized
def api_create_bit(user, user_id):
    data = request.get_json()
    bit = bit_service.save(data)
    return json_util.dumps(bit)

@bp.route('/@<user_id>/sync', methods=['get'])
@authorized
def api_sync(user, user_id):
    bit_service.sync(user_id)
    return 'OK'

@bp.route('/@<user_id>/bits/<bit_id>', methods=['get'])
def api_get_bit(user_id, bit_id):
    bit = bit_service.get(bit_id)
    return json_util.dumps(bit)


@bp.route('/user', methods=['get'])
def api_current_user():
    user = current_user()
    if user:
        return jsonify({
            'user_id': user['_id'],
            'authenticated': True
        })
    else:
        return handle_error('User is not authenticated', status=401)


@bp.route('/@<user_id>/bits/<bit_id>', methods=['delete'])
@authorized
def api_delete_bit(user, user_id, bit_id):
    # TODO: check auth user vs user_id
    deleted_id = bit_service.delete(bit_id)
    return jsonify({'deleted': deleted_id})