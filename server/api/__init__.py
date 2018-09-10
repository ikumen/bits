from .. import create_app as _create_app

def create_app(settings_override=None):
    """Creates API specific application instance"""
    return _create_app(__name__, __path__, settings_override)
