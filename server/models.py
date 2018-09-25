import logging

from collections import namedtuple
from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from .helpers import JSONSerializable


class GAEModel(JSONSerializable, ndb.Model):
    _default_indexed = False
    __model__ = None

    def __init__(self, **kwargs):
        super(GAEModel, self).__init__(**kwargs)
        if self.__model__ is None:
            raise TypeError('Model (__model__) is not defined!')

    @classmethod
    def id_to_key(cls, id):
        """Helper for converting id to model key.
        https://cloud.google.com/appengine/docs/standard/python/ndb/creating-entity-keys

        @param id identifier to convert to a key
        """
        return ndb.Key(cls, id)

    @classmethod
    def urlsafe_to_key(cls, urlsafe_key):
        """Helper for converting urlsafe key to model key.
        https://cloud.google.com/appengine/docs/standard/python/ndb/creating-entity-keys

        @param urlsafe_key urlsafe key string to convert to a key
        """
        return ndb.Key(urlsafe=urlsafe_key)

    @classmethod
    def _isinstance(cls, model, raise_error=True):
        """Check if given model is of same type as implementing class.

        @param model the model instance to check
        @param raise_error indicate if we should raise an error on type mismatch
        @returns True if model is instance of given class
        """
        result = isinstance(model, cls)
        if not result and raise_error:
            raise ValueError('%s is not of type %s' % (model, cls))
        return result

    @classmethod
    def create(cls, **kwargs):
        """Creates a new instance of implementing class and saves it.

        @param kwargs dictionary of params for creating new instance
        @returns saved instance
        """
        instance = cls(**kwargs)
        instance.put()
        return instance

    @classmethod
    def list(cls, parent_key=None, limit=50):
        """Returns all instances of implementing class.

        @param parent_key optional ancestor key to filter by
        @param limit optional fetch limit, defaults to 50
        """
        query = cls.query() if parent_key is None else cls.query(ancestor=ndb.Key(urlsafe=parent_key))
        return query.fetch(limit)

    @classmethod
    def get_by_key(cls, key):
        """Returns instance of implementing class identified by given urlsafe key.
        Key should be in urlsafe format, see:
        https://cloud.google.com/appengine/docs/python/ndb/creating-entities#Python_retrieving_entities

        @param key identifying key
        """
        try:
            return ndb.Key(urlsafe=key).get()
        except ProtocolBufferDecodeError:
            return None

    @classmethod
    def get_by_id(cls, id):
        """Returns instance of implementing class identified by given id.
        
        @param id identifier
        """
        try:
            return ndb.Key(cls, id).get()
        except ProtocolBufferDecodeError:
            return None

    @classmethod
    def update(cls, id, **kwargs):
        """update this instance to datastore.
        """
        upsert = kwargs.pop('upsert', False)
        model = cls.get_by_id(id)
        if model is None:
            if upsert is False:
                return None
            model = cls(id=id, **kwargs)
        else:        
            for k,v in kwargs.items():
                setattr(model, k, v)
        model.put()
        return model


    @classmethod
    def delete(cls, id):
        """Delete this instance from datastore.
        """
        cls.get_by_id(id).key.delete()

    def get_key(self):
        """Returns the key for this instance.
        https://cloud.google.com/appengine/docs/standard/python/ndb/creating-entity-keys
        """
        return self.key.urlsafe()

    def get_parent_key(self):
        """Returns this instance's parent key.
        """
        return self.key.parent().urlsafe()


    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        rv = self.to_dict()
        rv['id'] = self.id
        return rv

class DescendentModel(GAEModel):
    __parent__ = None
    def __init__(self, **kwargs):
        super(DescendentModel, self).__init__(**kwargs)
        if self.__parent__ is None:
            raise TypeError('Parent is not defined!')

    """For models that require an ancestor.
    """
    def _pre_put_hook(self):
        """Make sure all descendents have an ancestors.
        """
        if not isinstance(self.key.parent, self.__parent__):
            raise ValueError('Descendents require an ancestor (e.g. parent)')

    def to_json(self):
        rv = super(DescendentModel, self).to_json()
        rv['id'] = self.key.parent.id()
        return rv


class Setting(GAEModel):
    value = ndb.StringProperty(required=True, indexed=True)
        
class User(GAEModel):
    name = ndb.StringProperty()
    avatar_url = ndb.StringProperty()
    oauth = ndb.StringProperty(required=True, indexed=True)

class Bit(GAEModel):
    __parent__ = User

    title = ndb.StringProperty(required=True)
    content = ndb.StringProperty(required=True)
    tags = ndb.StringProperty(repeated=True)
    published_at = ndb.DateTimeProperty(indexed=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def update(cls, user_id, id, **kwargs):
        user_key = User.id_to_key(user_id)
        return super(Bit, cls).update(id, parent=user_key, **kwargs)


