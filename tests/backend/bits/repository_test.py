import backend
import pytest

from backend.bits import repository
from .. import DatastoreClientFactory, TestCaseWithGCPSupport

class TestBitRepository(TestCaseWithGCPSupport):
    def create_app(self):
        return backend.create_app()

    # @pytest.fixture
    # def bit_repo(self, app, with_datastore_client):
    #     return repository.BitRepository(with_datastore_client)

    def test_when_all_called_should_return_emtpy_list(self, app, with_datastore_client):
        print(repository.BitRepository(with_datastore_client).all())
        #print(bit_repo.all())