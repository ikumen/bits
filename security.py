import os

from functools import wraps
from flask import url_for, redirect, session, request, current_app
from requests_oauthlib import OAuth2Session, OAuth2Session


class OAuth():
	def __init__(self, config, oauth_token=None):
		self.config = config
		self.oauth_token = oauth_token
		self.session = self.create_oauth_session(config, oauth_token)

	@classmethod
	def create_oauth_session(cls, config, oauth_token): 
		return (cls.create_oauth1_session(config, oauth_token) 
			if config.get('VERSION') == '1.0' 
			else cls.create_oauth2_session(config, oauth_token))

	@classmethod
	def create_oauth1_session(cls, config, oauth_token):
		return OAuth1Session(config.get('CLIENT_KEY'),
			client_secret=config.get('CLIENT_SECRET'),
			callback_uri=config.get('CALLBACK_URL'),
			resource_owner_secret=oauth_token.get('SECRET'),
			resource_owner_key=oauth_token.get('KEY'))

	@classmethod
	def create_oauth2_session(cls, config, oauth_token):
		return OAuth2Session(config.get('CLIENT_KEY'),
			scope=config.get('SCOPE'),
			state=oauth_token,	
			redirect_uri=config.get('CALLBACK_URL'))

	def _fetch_oauth1_token(self, auth_response):
		verifier_token = self.session.parse_authorization_response(auth_response)
		return self.session.fetch_access_token(
			self.config.get('TOKEN_URL'),
			verifier=verifier_token.get('oauth_verifier'))

	def _fetch_oauth2_token(self, auth_response):
		return self.session.fetch_token(
			self.config.get('TOKEN_URL'),
			client_secret=self.config.get('CLIENT_SECRET'),
			authorization_response=auth_response)

	def authorize(self):
		# returns tuple of (auth_url, state)
		return self.session.authorization_url(
			self.config.get('AUTHORIZATION_URL'),
			approval_prompt='force',	# move to config
			include_granted_scopes='true')

	def fetch_token(self, auth_response):
		# TODO: raise exception if no access token
		oauth_resp = (self._fetch_oauth1_token(auth_response) if self.config.get('VERSION') == '1.0'
				else self._fetch_oauth2_token(auth_response))

		if not('oauth_token' in oauth_resp or 'access_token' in oauth_resp):
			# raise exception
			pass		
		return oauth_resp	

		


# ...............................
# Route helpers 
# ...............................
def get_session_oauth_token(oauth_config):
	return session.get(oauth_config.get('SESSION_KEY', oauth_config.get('NAME')))

def set_session_oauth_token(oauth_config, value):
	session[oauth_config.get('SESSION_KEY', oauth_config.get('NAME'))] = value

def load_oauth_config(provider):
	# TODO cache this or initialize at startup
	return current_app.config.get('OAUTHS', {}).get(provider)

def create_oauth(provider):
	oauth_config = load_oauth_config(provider)
	oauth_token = get_session_oauth_token(oauth_config)
	return OAuth(oauth_config, oauth_token)


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
		oauth_config = load_oauth_config(kwargs.get('provider'))
		if oauth_config.get('VERSION') == '1.0':
			pass
		else:
			oauth_token = get_session_oauth_token(oauth_config)
			if not (get_session_oauth_token(oauth_config) or \
					all(k in request.args for k in ('code', 'state')) or \
					request.args.get('state') == oauth_token):
				return abort(401)
		return fn(*args, **kwargs)
	return decorated_function


