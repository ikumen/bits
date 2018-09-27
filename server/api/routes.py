import logging

from bson import json_util
from flask import Blueprint, request, jsonify, Response
from ..helpers import handle_error
from ..security import authorized, current_user
from ..models import User
from ..services import UserService, BitService


bp = Blueprint('/api', __name__)
log = logging.getLogger(__name__)

@bp.route('/@<user_id>/bits', methods=['get'])
def list_bits(user_id):
    """Return bits for given user.
    """
    auth_user = current_user()
    if auth_user and auth_user['id'] == user_id:
        return jsonify(BitService.list(user_id, published_only=False))
    else:
        return jsonify(BitService.list(user_id))


@bp.route('/bits/<bit_id>', methods=['patch'])
@authorized
def update_bit(user, bit_id):
    bit_data = request.get_json() 
    BitService.update(bit_id, **bit_data)
    return Response(status=204)


@bp.route('/bits', methods=['post'])
@authorized
def create_bit(user):
    """Create and return a new blank bit for currently logged in user.
    """
    bit_data = request.get_json() or {} 
    bit = BitService.create(**bit_data)
    return jsonify(bit)


@bp.route('/bits/<bit_id>', methods=['get'])
def get_bit(bit_id):
    """Return the bit with given id.
    """
    bit = BitService.get(bit_id)
    if bit:
        return jsonify(bit)
    else:
        return Response(status=404)


@bp.route('/bits/<bit_id>', methods=['delete'])
@authorized
def api_delete_bit(user, bit_id):
    BitService.delete(bit_id)
    return Response(status=204)


@bp.route('/@<user_id>', methods=['get'])
def api_get_atuser(user_id):
    """Returns the profile of user currently being viewed (e.g. /@<some user>.
    """
    at_user = UserService.get(user_id).to_json()
    auth_user = current_user()
    if auth_user and auth_user['id'] == at_user['id']:
        at_user['is_auth'] = True
    return jsonify(at_user)


@bp.route('/user', methods=['get'])
def api_current_user():
    """Returns current authenticated user tied this session,
    otherwise indicate user is not logged in with 401.
    """
    user = current_user()
    if user:
        return jsonify(user)
    else:
        return Response(status=401)


@bp.route('/user/sync', methods=['get'])
@authorized
def api_sync(user):
    """Syncs local cache of bits with gist source by pulling all gists 
    for currently authenticated user."""
    BitService.sync(user.get('id'))
    return 'OK'
