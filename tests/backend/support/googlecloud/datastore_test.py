import backend
import pytest

from tests.backend import TestCaseWithGCPSupport
from backend.support import googlecloud


class MockGCModel(googlecloud.GCModel):
    _kind = 'Mock'


class TestGCModel(TestCaseWithGCPSupport):
    
    @pytest.fixture
    def with_mock_model(self, app):
        return MockGCModel().init_app(app)

    def test_setup(self, app, with_mock_model):
        print(len(with_mock_model.all()))


