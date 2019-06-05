from abc import ABCMeta, abstractmethod

class Repository(metaclass=ABCMeta):
    """Provides an interface for CRUD operations to be implemented 
    for a given type of entity.
    """
    @abstractmethod
    def init_app(self, app, **kwargs):
        pass

    @abstractmethod
    def upsert(self, **kwargs):
        pass

    @abstractmethod
    def get(self, id):
        pass

    @abstractmethod
    def all(self, filters=None, projection=None, order=None, limit=None, offset=0):
        pass

    @abstractmethod
    def delete(self, id):
        pass
