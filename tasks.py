"""
"""
import logging
import json
import yaml
import models
import utils
import dateutil.parser
import re

from google.appengine.api import urlfetch
from datetime import datetime
from slugify import slugify



class GistToPostConverter():

	# dict keys for gist
	_ID_ = 'id'
	_FILES_ = 'files'
	_CREATED_AT_ = 'created_at'
	_UPDATED_AT_ = 'updated_at'
	_TAGS_ = 'tags'
	_TITLE_ = 'title'


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


	def _make_slug(self, d, title):
		return ''.join([d.strftime('%Y/%m/%d/'), slugify(title)])

	
	def _has_markdown(self, gist):
		for fname in gist[self._FILES_]:
			if fname.endswith('.md'):
				return gist[self._FILES_][fname]
		return False


	def converts(self, user_id):
		"""Fetches all public gists for user with given user_id, then parse
		the gist to a corresponding post. Only public gist with markdown 
		file containing valid yaml frontmatter will be parsed. The resulting 
		post is really meta-data used by the front-end to build the actual 
		full post.
		"""
		# fetch all gists for given user
		gists = self._fetch(url=('https://api.github.com/users/'+ user_id +'/gists'))
		for gist in gists:
			# only convert gist that are public and have markdown
			if gist['public'] and self._has_markdown(gist):
				self._convert(gist[self._ID_])


	def _convert(self, gist_id):
		gist = self._fetch(url=('https://api.github.com/gists/' + gist_id))
		# TODO: for now we'll assume there's only 1 file
		markdown = self._has_markdown(gist)
		matches = re.search(r'^---(.*?)---\s*(.*)', markdown['content'], re.DOTALL)
		if matches:
			# our markdown should have a frontmatter block at beginning of file
			meta = yaml.load(matches.groups()[0])

			print(repr(meta))
			# let's assign some fallback values if they're 
			# missing in our frontmatter meta block
			# 
			# fallback to filename of markdown
			title = (meta[self._TITLE_] if self._TITLE_ in meta else markdown['filename']) 
			# fallback to gist created_at date
			created_at = models.normalize_datetime(gist[self._CREATED_AT_]) 
			if self._CREATED_AT_ in meta: 
				# unless created_at was explicitly set in frontmatter
				created_at = datetime.fromordinal(meta[self._CREATED_AT_].toordinal())

			# save our Post meta data
			models.Post(id=gist[self._ID_],
				title=title,
				slug=self._make_slug(created_at, title),
				created_at=created_at,
				updated_at=models.normalize_datetime(gist[self._CREATED_AT_]),
				tags=(meta[self._TAGS_] if self._TAGS_ in meta else []),
				file=markdown['raw_url']
			).put()



