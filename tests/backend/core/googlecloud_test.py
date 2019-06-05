import backend

from .. import TestCaseWithGCPSupport
from backend.support import DatastoreRepository


class TestDatastoreRepository(TestCaseWithGCPSupport):
    def create_app(self):
        return backend.create_app()

    def test_setup(self, app, with_datastore_client):
        MockDatastoreRepository(with_datastore_client)


class MockDatastoreRepository(DatastoreRepository):
    _entity = 'mock'
