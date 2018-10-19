import logging

from bson import json_util
from flask import Blueprint, request, jsonify, Response
from ..helpers import handle_error
from ..security import authorized, current_user
from ..models import User
from ..services import UserService, BitService


bp = Blueprint('/api', __name__)
log = logging.getLogger(__name__)

def __is_owner(user_id):
    auth_user = current_user()
    return auth_user and auth_user.get('id') == user_id


@bp.route('/@<user_id>/bits', methods=['get'])
def list_bits_by_user(user_id, published=True, is_owner=False):
    """Return bits for given user.
    """
    # limit to only titles
    if __is_owner(user_id):
        is_owner = True
        published = None # if it's owner, we don't care if published or not
    user = BitService.list_by_user(user_id, published=(None if is_owner else True))
    return jsonify({'user': user, 'isAuthUser': is_owner})


@bp.route('/@<user_id>/bits/<bit_id>', methods=['get'])
def get_bit(user_id, bit_id, published=True, is_owner=False):
    """Return the bit with given id.
    """
    if __is_owner(user_id):
        is_owner = True
        published = None # if it's owner, we don't care if published or not
    bit = BitService.get_by_user(bit_id, user_id, published=published)
    return jsonify({'bit': bit.to_json(include_user=True), 'isAuthUser': is_owner})


@bp.route('/@<user_id>/bits/<bit_id>', methods=['patch'])
@authorized
def update_bit(user, user_id, bit_id):
    is_owner = __is_owner(user_id)
    if is_owner:
        bit_data = request.get_json() 
        BitService.update(bit_id, user_id, **bit_data)
        return Response(status=204)
    return Response(status=401)


@bp.route('/@<user_id>/bits', methods=['post'])
@authorized
def create_bit(user, user_id):
    """Create and return a new blank bit for currently logged in user.
    """
    bit_data = request.get_json() or {} 
    bit = BitService.create(**bit_data)
    return jsonify({'bit': bit.to_json(include_user=True), 'isAuthUser': True})


@bp.route('/@<user_id>/bits/<bit_id>', methods=['delete'])
@authorized
def api_delete_bit(user, user_id, bit_id):
    is_owner = __is_owner(user_id)
    if is_owner:
        BitService.delete(bit_id, user_id)
        return Response(status=204)
    else:
        return Response(status=401)


@bp.route('/@<user_id>', methods=['get'])
def api_get_atuser(user_id):
    """Returns the profile of user currently being viewed (e.g. /@<some user>.
    """
    at_user = UserService.get(user_id)
    # User does not exists
    if at_user is None:
        return Response(status=404)

    # Exists, check if it's also the currently logged in user if they're logged in
    auth_user = current_user() # get a logged in user if there're on
    if auth_user and auth_user['id'] == at_user.id:
        at_user = at_user.to_json()
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
