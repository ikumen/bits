import importlib
import os
import pkgutil
import logging
import requests
import datetime

from flask import Flask, Blueprint, current_app
from flask_github import GitHub
from google.cloud import datastore
from .services import Users as _Users, Bits as _Bits
from .helpers import AppError, handle_error, EmulatorCredentials

# setup basic logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

# Create shared service instances
github = GitHub()
Users = _Users()
Bits = _Bits()

# Root of our application on filesystem
_app_path_ = os.path.dirname(os.path.abspath(__file__))


def _register_blueprints(app, pkg_name, pkg_path):
    """Register Blueprints for given package."""
    for _, name, _ in pkgutil.iter_modules(pkg_path):
        m = importlib.import_module('%s.%s' % (pkg_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)


def _load_config(app):
    app.config.from_pyfile('../.env')
    app.config.from_pyfile('../local.env', silent=True)


def _init_github(app):
    github.init_app(app)
    github.access_token_getter(lambda: Users.get(app.config.get('GITHUB_USER_ID'))['access_token'])


def _init_services(app, client=None):
    project = app.config.get('PROJECT_NAME')
    if app.config.get('ENV') == 'production':
        print('IN PRODUCTION !!!!!!!')
        client = datastore.Client(project=project)
    else:
        print('IN DEVELOPMENT !!!!!')
        client = datastore.Client(
            project=project,
            namespace=project,
            credentials=EmulatorCredentials(),
            _http=requests.Session(),
            _use_grpc=True)

        key = client.key('Task')
        task = datastore.Entity(key=key)
        print(key)
        task.update({
            'category': 'Personal',
            'done': False,
            'priority': 4,
            'description': 'Learn Cloud Datastore'
        })
        client.put(task)
        print(key)

    Users.init_app(client, app)
    Bits.init_app(client, github, app)
       

def create_app(override_settings=None):
    """Return a Flask application instance configured with defaults."""
    app = Flask(__name__, 
                template_folder='../dist', 
                static_folder='../dist/static', 
                static_url_path='/static')

    _load_config(app)
    _register_blueprints(app, __name__, __path__)
    _init_github(app)
    _init_services(app)

    app.errorhandler(AppError)(handle_error)

    return app

