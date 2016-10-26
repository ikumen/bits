import logging
import dateutil.parser
import yaml
import models
import tasks
import os
import mistune
import re
import utils

from flask import Flask, render_template, redirect, url_for, request, session, jsonify, Response
from google.appengine.ext import ndb, deferred
from google.appengine.api import urlfetch
from requests_oauthlib import OAuth2Session
from slugify import slugify

from datetime import datetime, date, time

app = Flask(__name__)

oauth = {
	'insecure_transport': models.Config.get(key='OAUTH_INSECURE_TRANSPORT'),
	'client_key': models.Config.get(key='OAUTH_CLIENT_KEY'),
	'client_secret': models.Config.get(key='OAUTH_CLIENT_SECRET')
}

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = oauth['insecure_transport']
app.secret_key = models.Config.get(key='APP_SECRET_KEY')

gist_post_converter = tasks.GistToPostConverter(
	access_token=models.Config.get(key='GH_OAUTH_TOKEN'))


@app.route('/manage/sync')
def manage_sync():
	# TODO: move user_id to config
	deferred.defer(gist_post_converter.converts, user_id='ikumen')
	return redirect(url_for('manage'))

@app.route('/signin')
def signin():
	oauth_session = OAuth2Session(oauth['client_key'],
		scope=['gist'],
		state=(session.get('github_oauth') if 'github_oauth' in session else None),
		redirect_uri='http://localhost:8080/oauth/complete')

	authorization_url, state = oauth_session.authorization_url(
		'https://github.com/login/oauth/authorize',
		approval_prompt='force',
		include_granted_scopes='true')

	session['github_oauth'] = state
	return redirect(authorization_url)


@app.route('/oauth/complete')
def signin_complete():
	os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
	if not 'github_oauth' in session or \
			not all(k in request.args for k in ('code', 'state')) or \
			request.args['state'] != session.get('github_oauth'):
		return abort(401)
	
	oauth_session = OAuth2Session(oauth['client_key'],
		scope=['gist'],
		state=(session.get('github_oauth') if 'github_oauth' in session else None),
		redirect_uri='http://localhost:8080/oauth/complete')

	oauth_resp = oauth_session.fetch_token(
		'https://github.com/login/oauth/access_token',
		client_secret=oauth['client_secret'],
		authorization_response=request.url)

	if 'access_token' not in oauth_resp:
		return abort(401)

	resource_oauth = {
		'token_type': oauth_resp['token_type'],
		'refresh_token': (oauth_resp['refresh_token'] if 'refresh_token' in oauth_resp else None),
		'access_token': oauth_resp['access_token']
	}

	results = oauth_session.get('https://api.github.com/user').json()
	user = models.User(id=results['login'],
		oauths=resource_oauth
	)
	user.put()
	print("-------------------> ")
	session['user'] = user.as_dict()
	return redirect(url_for('manage'))



@app.route('/')
def index():
	posts = models.Post.query().order(-models.Post.date)
	return render_template('index.html', posts=posts, now=date.today())


@app.route('/manage')
def manage():
	# dry, same snippet used in index()
	posts = models.Post.query().order(-models.Post.date)
	return render_template('manage.html', posts=posts, now=date.today())


@app.route('/manage/edit')
@app.route('/manage/edit/<id>')
def manage_edit(id=None):
	post_source = models.PostSource.get_by_id(int(id)) if id else None
	if post_source:
		post_source = post_source.as_dict()
	return render_template('edit.html', post_source=post_source)

#
# API methods
#

def api_response(data, mime='application/json', status=200):
	resp = jsonify(data)
	resp.mimetype = mime
	resp.status_code = status
	return resp


@app.route('/api/posts/<id>', methods=['GET'])
def api_post_get(id):
	"""Gets the PostSource with given id, otherwise a 404 response.
	"""
	post_source = models.PostSource.get_by_id(int(id)) if id else None
	if post_source:
		return api_response(data=post_source.as_dict())
	else:
		return api_response(data={'Err':'Not found'}, status=404)


@app.route('/api/posts', methods=['POST'])
@app.route('/api/posts/<id>', methods=['PUT'])
def api_post_save(id=None):
	data = request.get_json()
	if {'filename', 'content'} <= set(data):
		post_source = (ndb.Key(models.PostSource, int(id)).get() if id 
			else models.PostSource())
		post_source.filename = data['filename']
		post_source.content = data['content']
		post_source.put()
		deferred.defer(create_post, id=post_source.key.id())
		return api_response(data={'id': post_source.key.id()})
	else:
		return api_response(data={'Err': 'filename and content are required fields!'}, status=400)


@app.route('/api/publish/<id>', methods=['PUT'])
def api_publish(id):
	"""
	"""
	if id:
		id = int(id)
		data = request.get_json();
		post_source = models.PostSource.get_by_id(int(id))
		post_source.published = data['published']
		post_source.put()
		return api_response(data={'id': id, 'published': post_source.published})
	else:
		return api_response(data={'Err': 'Missing id of post to publish!'}, status=400)


def create_post(id):
	post_source = models.PostSource.get_by_id(id)
	matches = re.search(r'^---(.*?)---\s*(.*)', post_source.content, re.DOTALL)
	if matches:
		meta = yaml.load(matches.groups()[0])
		title = utils.default_if_not(meta['title'], post_source.filename)
		date = utils.date_to_datetime(meta['date'])
		models.Post(id=id,
			title=title,
			slug=''.join([date.strftime('%Y/%m/%d/'), slugify(title)]),
			date=date,
			tags=(meta['tags'] if 'tags' in meta else []),
			content=mistune.markdown(matches.groups()[1], escape=False, hard_wrap=True)
		).put()




@app.route('/tags')
def tags():
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
	post = models.Post.query(models.Post.slug == slug).get()
	return render_template('posts.html', post=post, now=date.today())


@app.route('/about')
def about():
	return render_template('about.html', now=date.today())


