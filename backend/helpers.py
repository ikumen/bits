from flask import json, request

MIME_TYPE_APPLICATION_JSON = 'application/json'
MIME_TYPE_TEXT_HTML = 'text/html'

__accepted_mimetypes = [MIME_TYPE_APPLICATION_JSON, MIME_TYPE_TEXT_HTML]


def use_json_mimetype():
    """Determine if 'application/json' is the preferred mimetype.
    """
    # http://flask.pocoo.org/snippets/45
    target = request.accept_mimetypes.best_match(__accepted_mimetypes)
    return (target == MIME_TYPE_APPLICATION_JSON and \
        request.accept_mimetypes[target] > request.accept_mimetypes[MIME_TYPE_TEXT_HTML])

class JSONSerializable(object):
    def to_json(self):
        pass

class JSONSerializableEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, JSONSerializable):
            return obj.to_json()
        return super(JSONSerializableEncoder, self).default(obj)