import os

from functools import wraps
from flask import url_for, redirect, session, request, current_app, abort
from requests_oauthlib import OAuth1Session, OAuth2Session

V1 = '1.0'
V2 = '2.0'
VERSION_KEY = 'VERSION'
STATE_SESS_KEY = 'STATE_SESSION_KEY'
TOKEN_SESS_KEY = 'TOKEN_SESSION_KEY'

class OAuth2Client():
	def __init__(self, config, state=None, token=None):
		self.oauth_config = config
		self.oauth_session = OAuth2Session(config.get('CLIENT_KEY'),
			scope=config.get('SCOPE'),
			state=state,
			token=token,
			redirect_uri=config.get('CALLBACK_URL'))

	def authorize(self):
		return self.oauth_session.authorization_url(
			self.oauth_config.get('AUTHORIZATION_URL'),
			approval_prompt='force',
			include_granted_scopes='true')

	def fetch_token(self, auth_resp): 
		return self.oauth_session.fetch_token(self.oauth_config.get('TOKEN_URL'),
			client_secret=self.oauth_config.get('CLIENT_SECRET'),
			authorization_response=auth_resp)

	def config(self, key, value=None):
		if value:
			self.oauth_config[key] = value
		return self.oauth_config.get(key)

	def get(self, path):
		return self.oauth_session.get(self.oauth_config.get('BASE_URL') + path)


def load_oauth_config(provider=None):
	return current_app.config.get('OAUTHS', {}).get(provider)

def create_oauth_client(provider):
	oauth_config = load_oauth_config(provider)
	if oauth_config.get(VERSION_KEY) == V2:
		return OAuth2Client(config=oauth_config,
			state=session.get(oauth_config.get(STATE_SESS_KEY)),
			token=session.get(oauth_config.get(TOKEN_SESS_KEY)))



# ...............................
# Decorators
# ...............................
def secured(fn):
	"""Decorator for applying very simple security check to see if user
	is signed in (checks to see if their in session).
	"""
	@wraps(fn)
	def decorated_function(*args, **kwargs):
		if 'user' not in session:
			return redirect(url_for('oops_unauthorized', next=request.url))
		return fn(*args, **kwargs)
	return decorated_function


def normalize_oauth_request(fn):
	"""Catch all for some hacks/tweaks to make OAuth work."""
	@wraps(fn)
	def decorated_function(*args, **kwargs):
		# force all provider ids coming in from url token to 
		# be upper case so it matches when config lookup by provider
		pkey = 'provider'
		kwargs[pkey] = (kwargs.get(pkey).upper() if pkey in kwargs else None)
		# for some reason oauthlib does not see this when it's 
		# defined after application declaration
		os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = current_app.config.get('OAUTHLIB_INSECURE_TRANSPORT')
		# this is work around for issue 
		# https://github.com/requests/requests-oauthlib/issues/157
		os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
		return fn(*args, **kwargs)
	return decorated_function


def oauth_authorized(fn):
	"""Decorator for oauth workflow that checks if user has 
	authorized us for access token.
	"""
	@wraps(fn)
	def decorated_function(*args, **kwargs):
		oauth_config = load_oauth_config(kwargs.get('provider', '').upper())
		if oauth_config.get(VERSION_KEY) == V2:
			if not any(k in session for k in (
					oauth_config.get(STATE_SESS_KEY),
					oauth_config.get(TOKEN_SESS_KEY))):
				return abort(401)
		else:
			pass
		return fn(*args, **kwargs)
	return decorated_function



