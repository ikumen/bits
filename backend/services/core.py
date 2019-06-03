import logging

from abc import ABCMeta
from google.cloud import datastore
from .. import helpers


log = logging.getLogger(__name__)


class DatastoreService(metaclass=ABCMeta):
    """
    Abstract class providing generic CRUD functionality around GCP datastore.
    """
    # Name of entity
    _entity = None
    # Name of identifier field
    _id = 'id'
    # Fields for this entity
    _fields = []
    _exclude_from_indexes = []

    def __init__(self, client=None):
        self._client = client

    def _key(self, id):
        """Create entity key for this this model and it's given id.
        """
        return self._client.key(self._entity, id)

    def _query(self):
        return self._client.query(kind=self._entity)

    def upsert(self, **kwargs):
        """Upsert an entity with the given attributes.
        """
        id = kwargs[self._id]
        # get existing or new
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
            msg = 'Unable to save %s: %s' % (self._entity, kwargs)
            log.error(msg, exc_info=1)
            raise helpers.AppError(msg) # pylint: disable=no-member

    def get(self, id):
        return self._client.get(self._key(id))

    def all(self, filters=None, projection=None, order=None, limit=None, offset=0, keys_only=False):
        query = self._query()
        for filter in filters or []:
            if len(filter) == 3:
                query.add_filter(*filter)

        if keys_only:
            query.keys_only()
            return list(query.fetch())
        else:
            if order:
                query.order = order
            if projection:
                query.projection = projection

        return list(query.fetch(limit=limit, offset=offset))

    def delete(self, id):
        self._client.delete(self._key(id))