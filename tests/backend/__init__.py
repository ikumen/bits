import os
import pytest
import json
import sys

from abc import ABCMeta, abstractmethod
from google.cloud import datastore
from flask import current_app
from backend.support.googlecloud import DatastoreClientFactory


class TestCase:
    def create_app(self): 
        pass 
        
    @pytest.fixture
    def app(self):
        app = self.create_app()
        with app.app_context():
            yield app

    @pytest.fixture
    def client(self, app):
        return app.test_client()


class TestCaseWithGCPSupport(TestCase):
    @pytest.fixture
    def with_datastore_client(self, app):
        project_name = app.config.get('PROJECT_NAME') or 'gnoht-bits'
        return DatastoreClientFactory.create_development_client(project_name)

