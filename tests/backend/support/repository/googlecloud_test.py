import backend

from tests.backend import TestCaseWithGCPSupport
from backend.support.repository import googlecloud


class MockDatastoreRepository(googlecloud.DatastoreRepository):
    _entity = 'mock'


class TestDatastoreRepository(TestCaseWithGCPSupport):
    def create_app(self):
        return backend.create_app()

    def test_setup(self, app, with_datastore_client):
        MockDatastoreRepository(with_datastore_client)


