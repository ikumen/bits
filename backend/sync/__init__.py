import logging

from flask import Blueprint
from .service import GitHubSyncService

sync_service = GitHubSyncService()
# define here so backend.__init__._register_blueprints can discover
bp = Blueprint('sync', __name__, url_prefix='/sync')

import backend.sync.routes
