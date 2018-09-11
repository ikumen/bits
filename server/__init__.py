import importlib
import logging
import pkgutil
import os

from flask import Flask, Blueprint
from flask.json import JSONEncoder
from .helpers import JSONSerializableEncoder
from .services import github


logger = logging.getLogger(__name__)


def _register_blueprints(app, pkg_name, pkg_path):
    """Register Blueprints for given package."""
    for _, name, _ in pkgutil.iter_modules(pkg_path):
        m = importlib.import_module('%s.%s' % (pkg_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)


def create_app(pkg_name, pkg_path, override_settings=None):
    """Return a Flask application instance configured with defaults."""
    app = Flask(pkg_name, template_folder='../../dist', static_folder='../../dist/static', static_url_path='/static')
    app.config.from_pyfile(__path__[0] + '/local.settings')
    github.init_app(app)
    app.json_encoder = JSONSerializableEncoder
    _register_blueprints(app, pkg_name, pkg_path)

    return app


