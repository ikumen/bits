import logging

from flask import jsonify, current_app, request, session
from werkzeug.exceptions import NotFound
from backend.support import security
from backend import support
from . import model as Bit, bp


log = logging.getLogger(__name__)


@bp.route('/bits', methods=['get'])
def all():
    bits = Bit.all_by_created_at()
    return jsonify(bits)
 
@bp.route('/bits/<id>', methods=['get'])
def get(id):
    log.info('id=%s' % id)
    bit = Bit.get(id)
    if bit is None:
        raise NotFound('No bit found with id: %s' % id)
    return jsonify(bit)

@bp.route('/bits', methods=['post'])
@security.authorized
def create():
    data = request.get_json()
    log.info('Creating new bit: %s' % data.get('description'))
    bit = Bit.save(data)
    return support.make_response(bit, status_code=201)

@bp.route('/bits/<id>', methods=['patch'])
@security.authorized
def update(id):
    log.info('Updating bit: %s' % id)
    data = request.get_json()
    data['id'] = id
    bit = Bit.update(**data)
    return support.make_response(bit, status_code=200)

# @bp.route('/bits/<id>', methods=['post', 'patch'])
# @security.authorized
# def save(id=None):
#     bit_data = request.get_json()
#     status_code = 201
#     if id and id != 'new':
#         # We're updating an existing bit
#         status_code = 200
#         bit_data.update({'id': id})

#     log.debug('About to save: %s' % (bit_data))
#     bit = Bit.save(bit_data)   
#     return support.make_response(bit, status_code=status_code)


@bp.route('/bits/<id>', methods=['delete'])
@security.authorized
def delete(id):
    Bit.delete(id)
    return support.make_response()

