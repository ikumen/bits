from flask import Blueprint
from .model import UserModel


model = UserModel()
bp = Blueprint('user', __name__, url_prefix='/api')

import backend.user.routes