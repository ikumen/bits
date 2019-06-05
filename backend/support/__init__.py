import json

from flask import current_app
from werkzeug.exceptions import InternalServerError

AUTHORIZED_SESSION_KEY = 'IS_AUTHORIZED'


def strftime(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def handle_error(error):
    """Return errors into appropriate Flask response"""
    payload = {'status_code': error.code, 'msg': error.description}
    return make_response(payload=payload, status_code=error.code)


def make_response(payload=None, status_code=200, mimetype='application/json', serialize=True):
    """Helper for making Flask response."""
    if payload is None:
        status_code = 204
    elif serialize:
        payload = json.dumps(payload)

    return current_app.response_class(
        response=payload,
        status=status_code,
        mimetype=mimetype)


class AppError(InternalServerError):
    pass
