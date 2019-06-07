import importlib
import os
import pkgutil
import logging
import requests
import datetime

from flask import Flask, Blueprint, current_app
from werkzeug.exceptions import HTTPException

from .support import github, security
from . import user, bit, support, sync


# setup basic logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

# Root of our application on filesystem
_app_path_ = os.path.dirname(os.path.abspath(__file__))


def _register_blueprints(app, pkg_name, pkg_path):
    """Register Blueprints for given package."""
    for _, name, _ in pkgutil.iter_modules(pkg_path):
        #log.debug('Importing %s.%s' % (pkg_name, name))
        m = importlib.import_module('%s.%s' % (pkg_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)


def _load_config(app):
    app.config.from_pyfile('../config/.env')
    app.config.from_pyfile('../config/production.env')
    app.config.from_pyfile('../config/local.env', silent=True)


def _init_services(app):
    github.init_app(app)
    user.model.init_app(app)
    bit.model.init_app(app)
    sync.sync_service.init_app(app)
       

def create_app(override_settings=None):
    """Return a Flask application instance configured with defaults."""
    app = Flask(__name__, 
                template_folder='../public', 
                static_folder='../public/static', 
                static_url_path='/static')

    _load_config(app)
    _register_blueprints(app, __name__, __path__)
    _init_services(app)

    # delegates all HTTPException based errors to support.handler_error 
    app.errorhandler(HTTPException)(support.handle_error)

    return app

