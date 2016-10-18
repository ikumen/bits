import logging
import dateutil.parser
import json
import yaml
import models
import tasks

from flask import Flask, render_template, redirect, url_for
from google.appengine.ext import ndb, deferred
from google.appengine.api import urlfetch

from datetime import datetime, date, time

app = Flask(__name__)

gist_handler = tasks.Gist(access_token=models.Config.get(key='GH_OAUTH_TOKEN'))

@app.route('/')
def index():
	deferred.defer(gist_handler.all, user_id='ikumen')
	return 'hello'

