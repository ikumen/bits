import logging
import json
import requests
import time

from abc import ABCMeta, abstractmethod
from flask.json import JSONEncoder
from google.auth import credentials
from google.cloud import datastore
from hashids import Hashids


log = logging.getLogger(__name__)


class IdGenerator:
    def __init__(self, app):
        self._hashids = Hashids(app.config.get('HASHIDS_SALT'))

    def get(self):
        return self._hashids.encode(int(round(time.time() * 1000)))


class EmulatorCredentials(credentials.Credentials):
    """Mock credential object. Copied from google-cloud-python 
    https://github.com/googleapis/google-cloud-python/blob/master/test_utils/test_utils/system.py
    """
    def __init__(self):
        self.token = b'seekrit'
        self.expiry = None

    @property
    def valid(self):
        return True

    def refresh(self, unused_request):
        raise RuntimeError('Should never be refreshed')


def _get_datastore_client(app):
    project_name = app.config.get('PROJECT_NAME')
    if app.config.get('ENV') == 'production':
        return datastore.Client(project=project_name)
    else:
        return datastore.Client(
            project=project_name,
            namespace=project_name,
            credentials=EmulatorCredentials(),
            _http=requests.Session(),
            _use_grpc=True)


class GCModel(metaclass=ABCMeta):
    _kind = None    # Kind of entity this model supports
    _id = 'id'      # Identifier for entity this model supports
    _fields = []    # Fields for the entity this model supports
    _exclude_from_indexes = [] # Fields we should not index
    _hashids = None

    def __init__(self, client=None, **kwargs):
        if self._kind is None:
            raise ValueError('Implementing classes should set _kind')
        self._client = client

    def init_app(self, app, **kwargs):
        if self._client is None:
            self._client = _get_datastore_client(app)
        if self._hashids is None:
            self._hashids = IdGenerator(app)
        return self
          
    def _key(self, id):
        """Create entity key"""
        if id is None:
            raise ValueError('"id" is required for all entities!')
        return self._client.key(self._kind, id)

    def _set_params(self, entity, kwargs):
        for k,v in kwargs.items():
            if k in self._fields:
                entity[k] = v

    def get(self, id):
        return self._client.get(self._key(id))

    def delete(self, id):
        return self._client.delete(self._key(id))

    def _init_entity(self, entity):
        """Allows hook for sub classes to initialize any default attributes for an entity."""
        return entity

    def new(self, kwargs):
        id = kwargs.get(self._id)
        if id is None:
            id = self._hashids.get()
            kwargs['id'] = id
        entity = datastore.Entity(key=self._key(id), exclude_from_indexes=self._exclude_from_indexes)
        self._init_entity(entity)
        self._set_params(entity, kwargs)
        return entity

    def update(self, upsert=True, **kwargs):
        print('Updating %s with %s' % (self._kind, kwargs))
        id = kwargs.get(self._id)
        with self._client.transaction():
            entity = self.get(id)
            if entity is None:
                if not upsert:
                    raise Exception('No %s found with id: %s' % (self._kind, id))
                entity = self.new(kwargs)
            else:
                self._set_params(entity, kwargs)
            entity = self.save(entity)
        return entity

    def save(self, entity):
        if not isinstance(entity, datastore.Entity):
            if not isinstance(entity, dict):
                raise TypeError('Only entity/dicts are supported! %s' % (type(entity)))
            entity = self.new(entity)
        self._client.put(entity)
        log.debug('Entity saved: %s' % (entity))
        return entity

    def _create_query(self):
        return self._client.query(kind=self._kind)

    def _apply_filters(self, query, filters):
        # Each filter should be a 3 item tuple (e.g. property, operator, value).
        # https://googleapis.github.io/google-cloud-python/latest/datastore/queries.html#google.cloud.datastore.query.Query.add_filter
        for filter in filters or []:
            if len(filter) == 3:
                query.add_filter(*filter)

    def get_by(self, filters):
        query = self._create_query()
        self._apply_filters(query, filters)
        rv = list(query.fetch(limit=1))
        if len(rv) == 0:
            return None
        return rv[0]

    def all(self, filters=None, projection=None, order=None, limit=None, offset=0, keys_only=False):
        """Peforms query on all entities supported by this model.
        """
        query = self._create_query()
        
        self._apply_filters(query, filters or [])

        if keys_only:
            query.keys_only()
            return list(query.fetch())
        else:
            if order:
                query.order = order
            if projection:
                query.projection = projection
        
        return list(query.fetch(limit=limit, offset=offset))

