from flask import Blueprint
from .repository import BitRepository

repository = BitRepository()
# define here so backend.__init__._register_blueprints can discover
bp = Blueprint('bits', __name__, url_prefix='/api')

import backend.bit.routes
