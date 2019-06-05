import importlib
import os
import pkgutil
import logging
import requests
import datetime

from flask import Flask, Blueprint, current_app
from werkzeug.exceptions import HTTPException
from google.cloud import datastore

from .support import github, security
from . import user, bit, support


# setup basic logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

# Root of our application on filesystem
_app_path_ = os.path.dirname(os.path.abspath(__file__))


def _register_blueprints(app, pkg_name, pkg_path):
    """Register Blueprints for given package."""
    for _, name, _ in pkgutil.iter_modules(pkg_path):
        log.debug('Importing %s.%s' % (pkg_name, name))
        m = importlib.import_module('%s.%s' % (pkg_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                log.debug('Found Blueprint in %s' % (name))
                app.register_blueprint(item)


def _load_config(app):
    app.config.from_pyfile('../.env')
    app.config.from_pyfile('../production.env')
    app.config.from_pyfile('../local.env', silent=True)


def _init_services(app):
    github.init_app(app)
    user.repository.init_app(app)
    bit.repository.init_app(app)
       

def create_app(override_settings=None):
    """Return a Flask application instance configured with defaults."""
    app = Flask(__name__, 
                template_folder='../public', 
                static_folder='../public/static', 
                static_url_path='/static')

    log.info('Creating app ...')
    _load_config(app)
    _register_blueprints(app, __name__, __path__)
    _init_services(app)

    # delegates all HTTPException based errors to support.handler_error 
    app.errorhandler(HTTPException)(support.handle_error)

    return app

