import backend
import pytest

from backend.bit import BitModel
from tests.backend import TestCaseWithGCPSupport

class TestBitModel(TestCaseWithGCPSupport):

    @pytest.fixture
    def with_bit_model(self, app):
        return BitModel().init_app(app)

    def test_when_all_called_should_return_emtpy_list(self, app, with_bit_model):
        print(len(with_bit_model.all()))
