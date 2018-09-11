import logging

from bson import json_util
from flask import Blueprint, request, jsonify
from ..security import authorized
from ..services import bit_service


bp = Blueprint('/api', __name__)
log = logging.getLogger(__name__)


@bp.route('/u:<user_id>/bits', methods=['get'])
def api_list_bits(user_id):
    bits = bit_service.list(filters={'user_id': user_id})
    return json_util.dumps(bits)


@bp.route('/u:<user_id>/bits', methods=['put'])
@authorized
def api_create_bit(user, user_id):
    data = request.get_json()
    bit = bit_service.save(data)
    return json_util.dumps(bit)


@bp.route('/u:<user_id>/bits/<bit_id>', methods=['get'])
def api_get_bit(user_id, bit_id):
    bit = bit_service.get(bit_id)
    return json_util.dumps(bit)


