import dateutil.parser

from google.appengine.ext import ndb

def normalize_datetime(d):
	return dateutil.parser.parse(d, ignoretz=True)


class AsDictionay():
	"""Helper for outputing model as serializable dictionary. ndb 
	already has a to_dict() function, but it does not include id
	which this helper includes in final output.
	"""
	def as_dict(self):
		d = super(type(self), self).to_dict()
		if self.key and self.key.id():
			d['id'] = self.key.id()
		return d


class User(ndb.Model, AsDictionay):
	name = ndb.StringProperty()
	oauths = ndb.JsonProperty()


class Post(ndb.Model, AsDictionay):
	"""Class representing raw blog post, where the content is a Jekyll 
	format text containing both meta frontmatter (e.g. date, tags, title)
	and the underlying content in markdown.
	"""
	slug = ndb.StringProperty()
	title = ndb.StringProperty()
	date = ndb.DateTimeProperty()	# date posted
	tags = ndb.StringProperty(repeated=True)
	content = ndb.TextProperty()
	published = ndb.BooleanProperty(default=False)
	# holds everything about post, frontmatter + markdown content
	source = ndb.TextProperty() 
	created_at = ndb.DateTimeProperty(auto_now_add=True)
	updated_at = ndb.DateTimeProperty(auto_now=True)


