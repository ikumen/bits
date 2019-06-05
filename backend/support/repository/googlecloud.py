import requests

from abc import ABCMeta
from .core import Repository
from google.auth import credentials
from google.cloud import datastore


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


class DatastoreClientFactory(object):
    """Create datastore client for production and development environments.
    """
    @classmethod
    def create_client(cls, app):
        project_name = app.config.get('PROJECT_NAME')
        if app.config.get('ENV') == 'production':
            return cls.create_production_client(project_name)
        else:
            return cls.create_development_client(project_name)

    @classmethod
    def create_production_client(cls, project_name):
        return datastore.Client(project=project_name)

    @classmethod
    def create_development_client(cls, project_name):
        print('creating development client')
        return datastore.Client(
            project=project_name,
            namespace=project_name,
            credentials=EmulatorCredentials(),
            _http=requests.Session(),
            _use_grpc=True)


class DatastoreRepository(Repository, metaclass=ABCMeta):
    """GCP datastore backed Repository implementation.
    """
    
    _entity = None  # name of target entity this repository supports (ie, kind)
    _id = 'id'      # name of target entity identifier field
    _fields = []    # target entity fields operated on by this repository

    _exclude_from_indexes = [] # fields we should NOT index

    def __init__(self, client=None):
        self._client = client
        if self._entity is None:
            raise AttributeError('Implementing class should set _entity')

    def init_app(self, app, **kwargs):
        super().init_app(app, **kwargs)
        if self._client is None:
            self._client = DatastoreClientFactory.create_client(app)

    def _key(self, id):
        """Creates GCP datastore key for target entity given 
        the following id.
        """
        return self._client.key(self._entity, id)

    def upsert(self, **kwargs):
        """Upsert the given args as a target entity, performing update if id
        is present in arguments or insert if not.
        """
        id = kwargs[self._id]
        try:
            with self._client.transaction():
                entity = self.get(id)
                if entity is None:
                    entity = datastore.Entity(key=self._key(id), exclude_from_indexes=self._exclude_from_indexes)
                for k,v in kwargs.items():
                    if k in self._fields:
                        entity.update({k: v})
                self._client.put(entity)
            return entity
        except:
            msg = 'Unable to upsert %s: %s' % (self._entity, kwargs)
            # TODO raise error

    def get(self, id):
        return self._client.get(self._key(id))

    def delete(self, id):
        return self._client.delete(self._key(id))

    def all(self, filters=None, projection=None, order=None, limit=None, offset=0, keys_only=False):
        """Peforms query on all entities supported by this Repository.
        """
        # build underlying Query object
        # https://googleapis.github.io/google-cloud-python/latest/datastore/queries.html
        query = self._client.query(kind=self._entity)

        # Each filter should be a 3 item tuple (e.g. property, operator, value).
        # https://googleapis.github.io/google-cloud-python/latest/datastore/queries.html#google.cloud.datastore.query.Query.add_filter
        for filter in filters or []:
            if len(filter) == 3:
                query.add_filter(*filter)

        if keys_only:
            query.keys_only()
            return list(query.fetch)
        else:
            if order:
                query.order = order
            if projection:
                query.projection = projection
        
        return list(query.fetch(limit=limit, offset=offset))
