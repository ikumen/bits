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
    user_with_bits = bit_service.list(user_id)
    _set_authenticated_flag(user_with_bits)
    return jsonify(user_with_bits)


@bp.route('/@<user_id>/bits/<bit_id>', methods=['patch'])
@authorized
def api_update_bit(user, user_id, bit_id):
    data = request.get_json()
    if bit_service.update(user_id, bit_id, **data):
        return jsonify({'updated': bit_id, 'status': 200})
    return handle_error('Bit not found', status=404)


@bp.route('/@<user_id>/bits', methods=['post'])
@authorized
def api_create_bit(user, user_id):
    """Create and return a new blank bit for currently logged in user.
    """
    data = request.get_json()
    bit = bit_service.create(user_id, **data)
    return json_util.dumps(bit)


@bp.route('/user/sync', methods=['get'])
@authorized
def api_sync(user):
    """Syncs local cache of bits with gist source by pulling all gists 
    for currently authenticated user."""
    bit_service.sync(user['_id'])
    return 'OK'


@bp.route('/@<user_id>/bits/<bit_id>', methods=['get'])
def api_get_bit(user_id, bit_id):
    """Return the bit with given id.
    """
    try:
        user_with_bit = bit_service.get(user_id, bit_id)
        _set_authenticated_flag(user_with_bit)
        return json_util.dumps(user_with_bit)
    except KeyError as err:
        return handle_error(err.message, status=404)


@bp.route('/@<user_id>', methods=['get'])
def api_get_atuser(user_id):
    """Returns the profile of user currently being viewed (e.g. /@<some user>.
    """
    user = user_service.get(user_id)
    return jsonify(_get_user_view_props(user))

def _set_authenticated_flag(user):
    auth_user = current_user()
    user['authenticated'] = (
        auth_user is not None and
        auth_user['_id'] == user['_id'])
    return user

def _get_user_view_props(user, auth_user=None):
    """Return a stripped down version of user appropriate for client.
    """
    user = {
        '_id': user['_id'],
        'avatar_url': user['avatar_url'],
        'name': user['name']}
    return _set_authenticated_flag(user)


@bp.route('/user', methods=['get'])
def api_current_user():
    """Returns the profile of current user of site if user is authenticated,
    otherwise indicate user is not logged in with 401.
    """
    user = current_user()
    if user:
        return jsonify(_get_user_view_props(user))
    else:
        return handle_error('User is not authenticated', status=401)


@bp.route('/@<user_id>/bits/<bit_id>', methods=['delete'])
@authorized
def api_delete_bit(user, user_id, bit_id):
    # TODO: check auth user vs user_id
    deleted_id = bit_service.delete(user_id, bit_id)
    return jsonify({'deleted': deleted_id})