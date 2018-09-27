import logging

from collections import namedtuple
from google.appengine.ext import ndb
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
from .helpers import JSONSerializable


class GAEModel(JSONSerializable, ndb.Model):
    _default_indexed = False

    def __init__(self, **kwargs):
        super(GAEModel, self).__init__(**kwargs)

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
    def create(cls, **kwargs):
        """Creates a new instance of implementing class and saves it.

        @param kwargs dictionary of params for creating new instance
        @returns saved instance
        """
        instance = cls(**kwargs)
        instance.put()
        return instance

    @classmethod
    def list(cls, limit=50):
        """Returns all instances of implementing class.

        @param parent_key optional ancestor key to filter by
        @param limit optional fetch limit, defaults to 50
        """
        query = cls.query()
        return query.fetch(limit)

    @classmethod
    def get(cls, id):
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
        model = cls.get(id)
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
        cls.get(id).key.delete()

    @property
    def id(self):
        return self.key.id()

    def to_json(self):
        rv = self.to_dict()
        rv['id'] = self.id
        return rv


class Setting(GAEModel):
    value = ndb.StringProperty(required=True, indexed=True)
        
class User(GAEModel):
    name = ndb.StringProperty()
    avatar_url = ndb.StringProperty()
    oauth = ndb.StringProperty(required=True, indexed=True)

    def to_json(self):
        """Returns the serializable JSON version of this model.
        NOTE: Flask uses this to serialize for jsonify and session.
        To prevent oauth token from being exposed to client (via jsonify)
        we remove it before being serialized.
        """
        rv = super(User, self).to_json()
        del rv['oauth'] # hide oauth from client view
        return rv


class Bit(GAEModel):
    user = ndb.KeyProperty(required=True, kind=User)
    title = ndb.StringProperty(required=True, default='')
    content = ndb.TextProperty(required=True, default='')
    tags = ndb.StringProperty(repeated=True)
    published_at = ndb.DateTimeProperty(indexed=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def update(cls, id, user_id, **kwargs):
        return super(cls, Bit).update(id, user=User.id_to_key(user_id), **kwargs)


