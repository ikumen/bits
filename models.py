import dateutil.parser

from google.appengine.ext import ndb

def normalize_datetime(d):
	return dateutil.parser.parse(d, ignoretz=True)


class Config(ndb.Model):
	"""Class representing application config in the form 
	of key/value pairs.
	"""

	# value of this config
	value = ndb.StringProperty()

	@classmethod	
	def get(cls, key):
		"""Returns the value for Config with given key. Creating 
		placeholder entry in datastore if key/value does not exists."""
		TODO = '_TODO_'
		config = ndb.Key(Config, key).get()
		if not config or config.value == TODO:
			# add placeholder, then alert developer
			config = Config(id=key, value=TODO)
			config.put()
			raise Exception('****  Config {} not found! Please use the ' +
				'Developers Console to enter missing config! ****'.format(key))

		return config.value


class AsDictionay():
	def as_dict(self):
		d = super(type(self), self).to_dict()
		if self.key and self.key.id:
			d['id'] = self.key.id()
		return d


class User(ndb.Model, AsDictionay):
	name = ndb.StringProperty()
	oauths = ndb.JsonProperty()


class PostSource(ndb.Model, AsDictionay):
	"""Class representing raw blog post, where the content is a Jekyll 
	format text containing both meta frontmatter (e.g. date, tags, title)
	and the underlying content in markdown.
	"""
	file_name = ndb.StringProperty()
	# holds everything about post, frontmatter + markdown content
	content = ndb.TextProperty() 
	created_at = ndb.DateTimeProperty()
	updated_at = ndb.DateTimeProperty()


class Post(ndb.Model, AsDictionay):
	"""Class representing publish blog post after it's been parsed from 
	a PostSource. Note: id of Post is PostSource.id as a Post cannot
	exists without an underlying PostSource.
	"""
	# url of this post in form of /posts/yyyy/mm/dd/title
	slug = ndb.StringProperty()
	title = ndb.StringProperty()
	date = ndb.DateTimeProperty()	# date posted
	tags = ndb.StringProperty(repeated=True)
	content = ndb.TextProperty()
