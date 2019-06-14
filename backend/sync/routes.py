import logging

from werkzeug.exceptions import Unauthorized
from functools import wraps
from flask import request
from backend import support
from backend import security
from . import sync_service, bp


log = logging.getLogger(__name__)

def app_engine_request(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get('X-Appengine-Cron') is None:
            raise Unauthorized()
        return f(*args, *kwargs)
    return decorated
        
@bp.route('/download')
@security.authorized
def download():
    synced_at = sync_service.download()
    return support.make_response(payload=dict(id='download', synced_at=synced_at))

@bp.route('/upload')
#@app_engine_request
def upload():
    sync_service.upload()
    return support.make_response(payload=dict(msg='OK'))
