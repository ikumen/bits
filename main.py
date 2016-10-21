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
	# TODO: move user_id to config
	deferred.defer(gist_post_converter.converts, user_id='ikumen')
	return redirect(url_for('index'))


@app.route('/')
def index():
	posts = models.Post.query().order(-models.Post.created_at)
	return render_template('index.html', posts=posts, now=date.today())


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


