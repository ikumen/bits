import logging
import requests

from datetime import datetime
from flask import Blueprint, current_app, session
from ..services import BitService, UserService
from ..security import OAUTH_ATTR_NAME


bp = Blueprint('tasks', __name__)

@bp.route('/sync/users', methods=['get'])
def sync_all_users():
	for user in UserService.list():
		__sync_bits_for_user(user)
	return 'OK'

def __sync_bits_for_user(user):
	with current_app.app_context():
		session[OAUTH_ATTR_NAME] = user.oauth
		# TODO: this is just a naive solution, possible race 
		# condition e.g. possible update between _fetch_all_from_github
		# and updating last_synced_at datetime.
		BitService._fetch_all_from_github(user.id, since=user.last_synced_at)
		UserService.update(user.id, last_synced_at=datetime.utcnow())
