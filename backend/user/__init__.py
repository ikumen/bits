from flask import Blueprint
from .repository import UserRepository


repository = UserRepository()
bp = Blueprint('user', __name__, url_prefix='/api')

import backend.user.routes