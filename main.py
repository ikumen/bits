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
import auth

from flask import Flask, render_template, redirect, abort, url_for, request, session, jsonify, Response, current_app
from google.appengine.ext import ndb, deferred
from google.appengine.api import urlfetch
from google.appengine.api import search
from requests_oauthlib import OAuth2Session
from slugify import slugify
from models import Post
from HTMLParser import HTMLParser
from datetime import datetime, date, time

app = Flask(__name__)

# ...............................
# Config
# ...............................
app.config.from_object(config.load())

# ...............................
# Auth related routes
# ...............................
@app.route('/signout')
def signout(code=200):
	session.clear()
	return redirect(url_for('index'))


@app.route('/signin/<provider>')
@auth.normalize_oauth_request
def signin(provider):
	oauth_client = auth.create_oauth_client(provider)
	# start oauth dance
	authorization_url, state = oauth_client.authorize()
	session[oauth_client.config('STATE_SESSION_KEY')] = state
	return redirect(authorization_url)


@app.route('/signin/<provider>/complete')
@auth.normalize_oauth_request
@auth.oauth_authorized
def signin_complete(provider):
	oauth_client = auth.create_oauth_client(provider)
	oauth_resp = oauth_client.fetch_token(auth_resp=request.url)

	if not 'access_token' in oauth_resp:
		# raise error
		pass

	session[oauth_client.config('TOKEN_SESSION_KEY')] = {
		'token_type': oauth_resp.get('token_type'),
		'access_token': oauth_resp.get('access_token'),
		'scope': oauth_resp.get('scope')
	}

	return redirect(url_for('signin_profile', provider=provider.lower()))


@app.route('/signin/<provider>/profile')
@auth.normalize_oauth_request
def signin_profile(provider=None):
	oauth_client = auth.create_oauth_client(provider)
	oauth_resp = oauth_client.get('/user')

	profile = oauth_resp.json()
	user_id = profile.get('id')
	user = models.User.get_by_id(user_id)

	if not user:
		user = models.User(id=user_id)
	if user.key.id() != int(oauth_client.config('USERID')):
		return abort(401)

	user.populate(name=profile.get('name')
		if profile.get('name') else profile.get('login'))
	user.put()

	session['user'] = user.as_dict()
	return redirect(url_for('manage'))



# ...............................
# Public routes
# ...............................
@app.route('/')
def index():
	"""Returns the home view with list of published posts.
	"""
	posts = (models.Post
		.query(models.Post.published == True, models.Post.category == 'posts')
		.order(-models.Post.date)
		# TODO:
		#.fetch(projection=['date', 'slug', 'title', 'tags'])
		)
	return render_template('index.html', posts=posts, now=date.today())


@app.route('/tags')
def tags():
	"""Returns the tags view with list of tags."""
	posts = (models.Post
		.query(models.Post.published == True, models.Post.category == 'posts')
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
	post = (Post
		.query(
			Post.published == True,
			Post.category == 'posts',
			Post.slug == slug)
		.get())
	return render_template('posts.html', post=post, now=date.today())


@app.route('/about')
def about():
	"""Returns about view.
	"""
	post = models.Post.query(models.Post.category == 'about').get()
	return render_template('about.html', post=post, now=date.today())


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
@auth.secured
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
@auth.secured
def api_post_save(id=None):
	"""Creates or updates the incoming data to a models.PostSource.
	"""
	data = request.get_json()
	if {'title', 'source'} <= set(data):
		post = models.Post.get_by_id(id) if id else models.Post()
		post.title = data['title']
		post.category = data['category'] if 'category' in data else 'posts'
		post.source = data['source']
		post.put()
		return api_response(data={'id': post.key.id()})

	else:
		return api_response(data={'Err': 'filename and content are required fields!'}, status=400)


# taken from here: http://stackoverflow.com/a/925630
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

kindle-27f8bb8af	192.168.19.125

@app.route('/api/publish/<int:id>', methods=['PUT'])
@auth.secured
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

		# normalize tags if missed by front matter or not in supported list format
		tags = []
		if 'tags' in meta:
			tags = (meta['tags'] if not isinstance(meta['tags'], basestring) \
				else [t.strip() for t in meta['tags'].split(',')])

		post.populate(
			date=pubdate,
			published=data['published'],
			slug=''.join([pubdate.strftime('%Y/%m/%d/'), slugify(post.title)]),
			tags=tags,
			content=content)
		post.put()

		if post.category == 'posts':
			# TODO: move to tasks
			doc = search.Document(
				doc_id=str(post.key.id()),
				fields=[search.TextField(name='title', value=post.title),
								search.TextField(name='slug', value=post.slug),
								search.TextField(name='published', value=str(post.published)),
								search.TextField(name='content', value=strip_tags(post.content))],
				language='en')

			try:
				results = search.Index(name='posts').put(doc)
			except search.Error as err:
				print(err)
				pass

		return api_response(data={'id': id, 'published': post.published})
	else:
		return api_response(data={'Err': 'Missing id of post to publish!'}, status=400)

@app.route('/manage')
@auth.secured
def manage():
	# dry, same snippet used in index()
	posts = (Post.query()
		.order(-models.Post.date)
		.fetch(projection=['title', 'published', 'date', 'created_at', 'updated_at']))
	return render_template('manage.html', posts=posts, now=date.today())


@app.route('/manage/edit')
@app.route('/manage/edit/<int:id>')
@auth.secured
def manage_edit(id=None):
	return render_template('edit.html')


@app.route('/search')
@app.route('/search/<terms>')
def search_posts(terms=None):
	if not terms:
		terms = request.args.get('terms', '')

	results = None
	try:
		index = search.Index(name='posts')
		query = search.Query(
			# very naive rough impl
			query_string='published: True AND (' + terms + ')',
			options=search.QueryOptions(
				returned_fields=['title', 'slug'],
				snippeted_fields=['content'],
		))
		results = index.search(query)
	except search.Error as err:
		print(err)
	return render_template('search.html', terms=terms, results=results, now=date.today())


# ...............................
# Errors
# ...............................
hn


