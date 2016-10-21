import logging
import dateutil.parser
import json
import yaml
import models
import tasks

from flask import Flask, render_template, redirect, url_for, request
from google.appengine.ext import ndb, deferred
from google.appengine.api import urlfetch

from datetime import datetime, date, time

app = Flask(__name__)

gist_post_converter = tasks.GistToPostConverter(
	access_token=models.Config.get(key='GH_OAUTH_TOKEN'))

@app.route('/admin/update')
def admin_update():
	deferred.defer(gist_post_converter.converts, user_id='ikumen')
	return redirect(url_for('index'))

@app.route('/')
def index():
	# TODO: move user_id to config
	#deferred.defer(gist_handler.all, user_id='ikumen')
	posts = models.Post.query().order(-models.Post.created_at)
	return render_template('index.html', posts=posts, now=date.today())




@app.route('/posts/<path:slug>')
def posts(slug):
	post = models.Post.query(models.Post.slug == slug).get()
	return render_template('posts.html', post=post, now=date.today())

@app.route('/about')
def about():
	return render_template('about.html', now=date.today())

'''

@app.route('/fetch')
def fetch():
	deferred.defer(fetch_gists)
	return redirect(url_for('index'))

@app.errorhandler(500)
def server_error(e):
	# log error and stacktrace
	logging.exception('Oops!')
	return 'Oops', 500



def update_gist(gist_id):
	result = urlfetch.fetch('https://api.github.com/users/ikumen/gists/' + gist_id,
		validate_certificate=True,
		headers={'Authorization': 'token '})
	if result.status_code == 200:
		print('--------------> ')
		print(result.content)


def fetch_gists(token):
	try:
		result = urlfetch.fetch('https://api.github.com/users/ikumen/gists', 
			validate_certificate=True,
			headers={'Authorization': 'token '})
		print('------- status')
		print(result.status_code)
		if result.status_code == 200:
			gists = json.loads(result.content)
			for gist in gists:
				if '.bits' in gist['files']:
					# .bits file contains meta data about this gists/post
					bits = yaml.load(gist['files']['.bits'])
					files = {}
					for file in gist['files']:
						files[gist['files'][file]['filename']] = {
							'name': gist['files'][file]['filename'],
							'url': gist['files'][file]['raw_url'],
							'size': gist['files'][file]['size']
						}

					gistModel = Gist(id=gist['id'],
						description=gist['description'],
						created_at=dateutil.parser.parse(gist['created_at'], ignoretz=True),
						updated_at=dateutil.parser.parse(gist['updated_at'], ignoretz=True),
						files=files)

					deferred.defer(update_gist, gist['id'])

					print('saving gist....')
					gistModel.put()
		else:
			print(result.status_code)
	except urlfetch.Error:
		logging.exception('Caught exception while fetching: https://api.github.com/users/ikumen/gists')

'''
