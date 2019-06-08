import logging

from flask import Blueprint
from backend import bit

bp = Blueprint('tasks', __name__, url_prefix='/tasks')
log = logging.getLogger(__name__)

@bp.route('/upload')
def upload_bits():
    #bits.repository.upload_modified_to_github()
    return 'OK'