import logging

from flask import jsonify, current_app, request, session
from werkzeug.exceptions import NotFound
from backend.support import security
from backend import support
from . import model as Bit, bp


log = logging.getLogger(__name__)


@bp.route('/bits', methods=['get'])
def all():
    bits = Bit.all_partial_public() \
        if session.get(support.AUTHORIZED_SESSION_KEY) is None \
        else Bit.all_partial()
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

@bp.route('/bits/<id>', methods=['delete'])
@security.authorized
def delete(id):
    Bit.delete(id)
    return support.make_response()

