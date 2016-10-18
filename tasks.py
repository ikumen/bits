"""
"""
import logging
import json
import yaml
import models
import utils
import dateutil.parser

from google.appengine.api import urlfetch
from datetime import datetime

class Gist():

	def __init__(self, access_token):
		self.access_token = access_token


	def _fetch(self, url):
		"""Helper/wrapper for making calls via urlfetch. Handles setting headers
		and parsing response json data.
		"""
		try:
			resp = urlfetch.fetch(url, validate_certificate=True, 
				headers={'Authorization': 'token ' + self.access_token})
			if resp.status_code == 200:
				return json.loads(resp.content)
			else:
				return resp.status_code
		except urlfetch.Error:
			logging.exception('Unable to fetch: {}'.format(url))


	def all(self, user_id):
		"""Fetches all public gists for user with given id.
		"""
		gists = self._fetch(url=('https://api.github.com/users/'+ user_id +'/gists'))
		for gist in gists:
			if gist['public'] and '.bits' in gist['files']:
				self.get(gist['id'])


	def get(self, id):
		"""Fetch the gist with given id. If the return gist is public and has a 
		'.bits' file, then it represents a post, so parse it and save the meta
		data.
		"""

		# json loaded representation of gist data from github
		gist = self._fetch(url=('https://api.github.com/gists/' + id))
		# meta data from .bits in yaml format
		meta = yaml.load(gist['files']['.bits']['content']) 

		# yaml converts the date as datetime.date, we use
		# datetime in our models
		if meta['date']:
			meta['date'] = datetime.fromordinal(meta['date'].toordinal()) 

		# build up a list of meta-data about each file in the gist
		files = {}
		for file in gist['files']:
			files[gist['files'][file]['filename']] = {
				'name': gist['files'][file]['filename'],
				'url': gist['files'][file]['raw_url'],
				'size': gist['files'][file]['size']
			}

		# save all the meta data and relevant to build a post
		models.Post(id=gist['id'],
			title=utils.defaultIfNone(meta['title'], gist['description']),
			created_at=utils.defaultIfNone(meta['date'], 
				models.normalize_datetime(gist['created_at'])),
			updated_at=models.normalize_datetime(gist['updated_at']),
			files=files
		).put()

