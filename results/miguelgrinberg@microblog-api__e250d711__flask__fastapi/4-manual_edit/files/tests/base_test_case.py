import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.app import create_app, db
from api.models import User
from config import Config


class TestConfig(Config):
    SERVER_NAME = 'localhost:5000'
    TESTING = True
    DISABLE_AUTH = True
    ALCHEMICAL_DATABASE_URL = 'sqlite://'


class TestConfigWithAuth(TestConfig):
    DISABLE_AUTH = False
    REFRESH_TOKEN_IN_BODY = True
    OAUTH2_PROVIDERS = {
        'foo': {
            'client_id': 'foo-id',
            'client_secret': 'foo-secret',
            'authorize_url': 'https://foo.com/login',
            'access_token_url': 'https://foo.com/token',
            'get_user': {
                'url': 'https://foo.com/me',
                'email': lambda json: json['email'],
            },
            'scopes': ['user', 'email'],
        },
    }
    OAUTH2_REDIRECT_URI = 'http://localhost/oauth2/{provider}/callback'


class BaseTestCase(unittest.TestCase):
    config = TestConfig

    def setUp(self):
        # Create the FastAPI app
        self.app = create_app(self.config)
        
        # Use FastAPI's TestClient
        self.client = TestClient(self.app)
        
        # Set up the database
        db.create_all()
        user = User(username='test', email='test@example.com', password='foo')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        # Tear down the database
        db.session.close()
        db.drop_all()
