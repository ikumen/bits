import logging
import dateutil.parser
import yaml
import models
import tasks
import os
import mistune
import re
import utils
import config
import security

from flask import Flask, render_template, redirect, url_for, request, session, jsonify, Response
from google.appengine.ext import ndb, deferred
from google.appengine.api import urlfetch
from requests_oauthlib import OAuth2Session
from slugify import slugify


from datetime import datetime, date, time

app = Flask(__name__)

# ...............................
# Config
# ...............................
app.config.from_object(config.load())




@app.route('/signin/<provider>')
@security.normalize_oauth_request
def signin(provider):
	oauth = security.create_oauth(provider)
	authorization_url, state = oauth.authorize()
	security.set_session_oauth_token(oauth.config, state)
	return redirect(authorization_url)


@app.route('/signin/<provider>/complete')
@security.normalize_oauth_request
@security.oauth_authorized
def signin_complete(provider):
	oauth = security.create_oauth(provider)
	oauth_resp = oauth.fetch_token(request.url)
	
	print("-----------> ")
	print(oauth_resp)

	# resource_oauth = {
	# 	'token_type': oauth_resp['token_type'],
	# 	'refresh_token': (oauth_resp['refresh_token'] if 'refresh_token' in oauth_resp else None),
	# 	'access_token': oauth_resp['access_token']
	# }

	# results = oauth_session.get('https://api.github.com/user').json()
	# user = models.User(id=results['login'],
	# 	oauths=resource_oauth
	# )
	# user.put()
	# session['user'] = user.as_dict()
	return redirect(url_for('manage'))


# ...............................
# Public routes
# ...............................
@app.route('/')
def index():
	"""Returns the home view with list of published posts.
	"""
	posts = models.Post.query(models.Post.published == True).order(-models.Post.date)
	return render_template('index.html', posts=posts, now=date.today())


@app.route('/tags')
def tags():
	"""Returns the tags view with list of tags."""
	posts = (models.Post.query()
		.order(models.Post.tags)
		.fetch(projection=['title', 'slug', 'tags']))
	# TODO: OrderedDict?
	tags_posts = {}
	tags = []
	for post in posts:
		for tag in post.tags:
			if tag not in tags_posts:
				tags_posts[tag] = []
				tags.append(tag)
			tags_posts[tag].append(post)
	# TODO: DRY now creation/cache for jinja
	return render_template('tags.html', tags=tags, tags_posts=tags_posts, now=date.today())


@app.route('/posts/<path:slug>')
def posts(slug):
	"""Returns individual post view with published post with given slug.
	"""
	post = models.Post.query(models.Post.slug == slug).get()
	return render_template('posts.html', post=post, now=date.today())


@app.route('/about')
def about():
	"""Returns about view.
	"""
	return render_template('about.html', now=date.today())


# ...............................
# API routes
# ...............................
def api_response(data, mime='application/json', status=200):
	"""Helper for return jsonify response.
	"""
	resp = jsonify(data)
	resp.mimetype = mime
	resp.status_code = status
	return resp


def parse_front_matter(source, is_fm_only=True):
	"""Parses the given yaml front matter into a meta dictionary
	with info about underlying post. Expects only a front matter
	snippet. If you need to parse a complete Jekyll style document
	that may contain markdown in addition to the front matter,
	then set is_fm_only to False.
	"""
	if not is_fm_only:
		source, mk = parsables_from_source(source)
	return yaml.load(source) if source else None


def parse_markdown(source, is_mk_only=True):
	"""Parses the given markdown into html. Expects only a markdown
	document. If you need to parse a complete Jekyll document that
	may contain yaml front matter in addition to the markdown, then
	set is_mk_only to False.
	"""
	if not is_mk_only:
		fm, source = parsables_from_source(source)
	return mistune.markdown(source, escape=False, hard_wrap=True) if source else None


def parsables_from_source(source):
	"""Splits the yaml front matter and markdown into parsable parts
	from the given source. The source is expected to be in Jekyll 
	document format.
	
	Returns tuple of (frontmatter, markdown)
	"""
	matches = re.search(r'^---(.*?)---\s*(.*)', source, re.DOTALL)
	if matches:
		return (matches.groups()[0], 
			(matches.groups()[1] if len(matches.groups()) >= 2 else None))
	return (None, None)


def post_from_source(source):
	"""Parses given source into a Post with meta dictionary parsed 
	from yaml front matter and rendered html from markdown.
	"""
	fmatter, markdown = parsables_from_source(source)
	return (parse_front_matter(fmatter), parse_markdown(markdown))


@app.route('/api/posts/<int:id>', methods=['GET'])
def api_post_get(id):
	"""Gets the PostSource with given id, otherwise a 404 response.
	Called from /manage/edit/<id> page.
	"""
	post = models.Post.get_by_id(id) if id else None
	if post:
		return api_response(data=post.as_dict())
	else:
		return api_response(data={'Err':'Not found'}, status=404)


@app.route('/api/posts', methods=['POST'])
@app.route('/api/posts/<int:id>', methods=['PUT'])
def api_post_save(id=None):
	"""Creates or updates the incoming data to a models.PostSource.
	"""
	data = request.get_json()
	if {'title', 'source'} <= set(data):
		post = models.Post.get_by_id(id) if id else models.Post()
		post.title = data['title']
		post.source = data['source']
		post.put()
		return api_response(data={'id': post.key.id()})

	else:
		return api_response(data={'Err': 'filename and content are required fields!'}, status=400)


@app.route('/api/publish/<int:id>', methods=['PUT'])
def api_publish(id):
	"""
	"""
	if id:
		data = request.get_json();
		post = models.Post.get_by_id(id)
		meta, content = post_from_source(post.source)

		# rules for publish date: 
		#		- if 'date' set by user in front matter then use it
		#		- else if pubdate is already set, use it
		#		- else must be first time saving, use todays date
		pubdate = post.date
		if 'date' in meta:
			pubdate = utils.date_to_datetime(meta['date'])
		elif not pubdate:
			pubdate = datetime.today()

		post.populate(
			date=pubdate,		
			published=data['published'],
			slug=''.join([pubdate.strftime('%Y/%m/%d/'), slugify(post.title)]),
			tags=(meta['tags'] if 'tags' in meta else []),
			content=content)
		post.put()

		return api_response(data={'id': id, 'published': post.published})
	else:
		return api_response(data={'Err': 'Missing id of post to publish!'}, status=400)


@app.route('/oops/unauthorized')
def oops_unauthorized():
	return render_template('401.html', now=date.today())


@app.route('/manage')
@security.secured
def manage():
	# dry, same snippet used in index()
	posts = models.Post.query().order(-models.Post.date)
	return render_template('manage.html', posts=posts, now=date.today())


@app.route('/manage/edit')
@app.route('/manage/edit/<int:id>')
@security.secured
def manage_edit(id=None):
	post = models.Post.get_by_id(id) if id else None
	if post:
		post = post.as_dict()
	return render_template('edit.html', post=post)

