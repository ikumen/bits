import logging

from bson import json_util
from flask import Blueprint, request, jsonify
from ..security import authorized
from ..services import bit_service


bp = Blueprint('/api', __name__)
log = logging.getLogger(__name__)


@bp.route('/<user_id>/', methods=['get'])
@authorized
def api_list_bits(user, user_id):
    bits = bit_service.list({'user_id': user_id})
    return json_util.dumps(bits)


@bp.route('/<user_id>', methods=['put'])
@authorized
def api_create_bit(user, user_id):
    data = request.get_json()
    bit_service.save(data)
    return 'foobar'


