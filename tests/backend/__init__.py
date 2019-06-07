import os
import pytest
import json
import sys

from abc import ABCMeta, abstractmethod
from google.cloud import datastore
from flask import current_app
from backend import create_app
from backend.support import googlecloud


def make_headers(**kwargs):
    """Makes headers with the given arguments, along with some defaults."""
    headers = {'Content-Type': 'application/json'}
    headers.update(**kwargs)
    return headers


def assert_valid_response(resp, status_code=200, content_type='application/json'):
    """Utility to assert the expected responsed"""
    assert resp.status_code == status_code
    assert resp.content_type == content_type

def create_test_app():
    app = create_app()
    app.config.from_pyfile('../config/test.env')
    return app


class TestCase:
    def create_app(self): 
        return create_test_app()
        
    @pytest.fixture
    def app(self):
        app = self.create_app() # pylint: disable=assignment-from-no-return
        with app.app_context():
            yield app

    @pytest.fixture
    def client(self, app):
        return app.test_client()


class TestCaseWithGCPSupport(TestCase):
    pass

