import os

from functools import wraps
from flask import url_for, redirect, session, request, current_app, abort
from requests_oauthlib import OAuth2Session, OAuth2Session


def load_oauth_config(provider=None):
	return current_app.config.get('OAUTHS', {}).get(provider)

def create_oauth(provider, state=None, token=None):
	oauth_config = load_oauth_config(provider)
	return oauth_config, create_oauth_session(
		config=oauth_config, token=token, state=state)

def create_oauth_session(config, token=None, state=None):
	return OAuth2Session(config.get('CLIENT_KEY'),
			scope=config.get('SCOPE'), 
			state=state,
			token=token,
			redirect_uri=config.get('CALLBACK_URL'))

def oauth_authorize(config, oauth_session):
	return oauth_session.authorization_url(config.get('AUTHORIZATION_URL'),
			approval_prompt='force', 
			include_granted_scopes='true')


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
			if not any(k in session for k in (
					oauth_config.get('STATE_SESSION_KEY'),
					oauth_config.get('TOKEN_SESSION_KEY'))):
				print('print aborting')
				return abort(401)
		return fn(*args, **kwargs)
	return decorated_function



