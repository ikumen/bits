import logging
import dateutil.parser
import json
import yaml
import models
import tasks
import os

from flask import Flask, render_template, redirect, url_for, request, session
from google.appengine.ext import ndb, deferred
from google.appengine.api import urlfetch
from requests_oauthlib import OAuth2Session

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
	posts = models.Post.query().order(-models.Post.created_at)
	return render_template('index.html', posts=posts, now=date.today())


@app.route('/manage')
def manage():
	# dry, same snippet used in index()
	posts = models.Post.query().order(-models.Post.created_at)
	return render_template('manage.html', posts=posts, now=date.today())


@app.route('/manage/edit')
@app.route('/manage/edit/<id>')
def manage_edit(id=None):
	post = ndb.Key(models.Post, id).get() if id else None
	return render_template('edit.html', post=post)


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


