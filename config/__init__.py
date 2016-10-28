'''Provides functionality for loading Yaml based configurations into a 
Flask config. The loading functionality tries to load three levels of 
configurations in the following order, with the latter configurations
overriding the earlier configurations.

	1. default - should contain default configurations applicable to all 
			environments. By default it looks for "./config/default.yml" file.
	2. environment - should contain environment specific (e.g. dev, prod,...) 
			configuration. You can pass a path to the environment specific config 
			when calling load (e.g, env_config=/some/path.yml) or supply it
			with the name of an OS environment variable that contains the path to
			your config (e.g env_config=MY_APP_CONFIG). By default no value is specified.
	3. local - contains environment specific configurations that are too
			sensitive to check into source control. By default it looks for 
			"./instance/local.yml" file.

	*Note: default, environment, and local can all be define to point to any
	custom path accessible by main calling program.

Example 1: defaults with no environment specific config

	import config
	from flask import Flask, ...

	app = Flask()
	app.config.from_object(config.load())

Example 2: default, plus environment specific and sensitive configs
	
	...
	app = Flask
	app.config.from_object(
		config.load(
			env_config='config/production.yml',
			local_config='somewhere/not/in/git/secrets.yml'
	))

Example 3: default, plus environment specific (but using OS environment var)

	# export MY_APP_CONFIG=config/test.yml

	app = Flask
	app.config.from_object(config.load(env_config='MY_APP_CONFIG'))

'''
import os
import yaml

from collections import namedtuple
from google.appengine.ext import ndb


class Config(ndb.Model):
	"""Class representing application config in the form of key/value pairs,
	for use with Google App Engine Datastore. Model's id will serve as the 
	configuration key name.
	"""
	# value of this config
	value = ndb.StringProperty()

	@classmethod	
	def get(cls, key):
		"""Returns the value for Config with given key. Creating 
		placeholder entry in datastore if key/value does not exists."""
		PLACEHOLDER = '__REPLACE_ME__'
		config = ndb.Key(Config, key).get()
		if not config or config.value == PLACEHOLDER:
			# add placeholder, then alert developer
			config = Config(id=key, value=PLACEHOLDER)
			config.put()
			raise Exception('Config {} not found! Please use the Developers Console to enter missing config!'.format(key))
		return config.value


	@classmethod
	def sget(cls, key):
		"""Wrapper for get() that fails silently."""
		try:
			return cls.get(key)
		except Exception as e:
			print(e)
			pass
		return None 


class Struct:
	"""Wraps our dict of configuration attributes into an object 
	for Flask's config.from_object function.
	"""
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)


def _merge_configs(target, source):
	"""Merges two dictionaries, overriding any values in 'target' dict 
	with values from "source" dict for any values with the same keys in
	both dictionaries. The overriding stops at any non-dict child value.
	Note: 'target' is modified in the merging process, unless it was None.
	"""
	if isinstance(target, dict) and isinstance(source, dict):
		for k,v in source.items():
			# keep traversing child values if dict type
			target[k] = _merge_configs(target[k], v) if k in target else v
	elif isinstance(source, dict):
		target = source
	return target


def _resolve_missing_vals(keys, target):
	"""Iterate the target's attributes and resolve any missing values.
	Values not found by Config.sget() are set up with placeholders in
	datastore for client to fill in.
	"""
	if isinstance(target, dict):
		for k,v in target.items():
			keys.append(''.join(['_', k]))
			if not v:
				k = Config.sget((''.join(keys))[1:])
			elif hasattr(v, '__iter__'):
				_resolve_missing_vals(keys, v)
			keys.pop()
	elif isinstance(target, list):
		for item in target:
			_resolve_missing_vals(keys, item)


def _load_config(path):
	"""Loads the yaml config at the given path, otherwise nothing 
	(i.e, fails silently) if there was an error.
	"""
	if path:
		try:
			with open(path) as f:
				return yaml.load(f)
		except(IOError, yaml.YAMLError) as e:
			print(e)
			pass
	return None


def load(default_config='config/default.yml', 
	env_config=None):
	"""Attempts to load 3 levels of configuration, with latter configurations
	overriding formerly set values, then returns it as an object to be 
	consumed by Flask's config.from_object function.
	"""
	# we'll assume env_config points to an OS environment 
	# variable if it doesn't look like a file path
	if env_config and not env_config.ends('.yml'):
		env_config = os.getenv(env_config)

	# see module comments above on what's happening here
	configs = _merge_configs(_merge_configs({},
			_load_config(default_config)),
			_load_config(env_config))

	_resolve_missing_vals([], configs)

	return Struct(**configs)

