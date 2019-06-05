import os
import pytest
import json
import sys

from abc import ABCMeta, abstractmethod
from google.cloud import datastore
from flask import current_app
from backend.support.repository import googlecloud

def make_headers(**kwargs):
    """Makes headers with the given arguments, along with some defaults."""
    headers = {'Content-Type': 'application/json'}
    headers.update(**kwargs)
    return headers


def assert_valid_response(resp, status_code=200, content_type='application/json'):
    """Utility to assert the expected responsed"""
    assert resp.status_code == status_code
    assert resp.content_type == content_type


class TestCase:
    def create_app(self): 
        pass 
        
    @pytest.fixture
    def app(self):
        app = self.create_app() # pylint: disable=assignment-from-no-return
        with app.app_context():
            yield app

    @pytest.fixture
    def client(self, app):
        return app.test_client()


class TestCaseWithGCPSupport(TestCase):
    @pytest.fixture
    def with_datastore_client(self, app):
        project_name = app.config.get('PROJECT_NAME') or 'gnoht-bits'
        return googlecloud.DatastoreClientFactory.create_development_client(project_name)

