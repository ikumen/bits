import logging

from bson import json_util
from flask import Blueprint, request, jsonify
from ..helpers import handle_error
from ..security import authorized, current_user
from ..services import bit_service, user_service


bp = Blueprint('/api', __name__)
log = logging.getLogger(__name__)


@bp.route('/@<user_id>/bits', methods=['get'])
def api_list_bits(user_id):
    """Return bits for given user.
    """
    bits = bit_service.list(filters={'user_id': user_id})
    return json_util.dumps(bits)


@bp.route('/bits', methods=['put', 'post'])
@authorized
def api_create_bit(user):
    """Create and return a new blank bit for currently logged in user.
    """
    data = request.get_json()
    bit = bit_service.create(user, data=data)
    return json_util.dumps(bit)


@bp.route('/user/sync', methods=['get'])
@authorized
def api_sync(user):
    """Syncs local cache of bits with gist source by pulling all gists 
    for currently authenticated user."""
    bit_service.sync(user['_id'])
    return 'OK'


@bp.route('/bits/<bit_id>', methods=['get'])
def api_get_bit(bit_id):
    """Return the bit with given id.
    """
    bit = bit_service.get(bit_id)
    return json_util.dumps(bit)


@bp.route('/@<user_id>', methods=['get'])
def api_get_atuser(user_id):
    """Returns the profile of user currently being viewed (e.g. /@<some user>.
    """
    user = user_service.get(user_id)
    return jsonify({
        '_id': user['_id'],
        'avatar_url': user['avatar_url'],
        'name': user['name'],
        'authenticated': False
    })


@bp.route('/user', methods=['get'])
def api_current_user():
    """Returns the profile of current user of site if user is authenticated,
    otherwise indicate user is not logged in with 401.
    """
    user = current_user()
    if user:
        return jsonify({
            '_id': user['_id'],
            'avatar_url': user['avatar_url'],
            'name': user['name'],
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