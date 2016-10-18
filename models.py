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



class Post(ndb.Model):
	"""Class representing a blog post. Underlying data for each 
	post is composed of gist data.
	"""

	# url of this post in form of /posts/yyyy/mm/dd/title
	slug = ndb.StringProperty()
	title = ndb.StringProperty()
	# date created/updated
	created_at = ndb.DateTimeProperty()
	updated_at = ndb.DateTimeProperty()
	# all the files that make up this post		
	files = ndb.JsonProperty()
