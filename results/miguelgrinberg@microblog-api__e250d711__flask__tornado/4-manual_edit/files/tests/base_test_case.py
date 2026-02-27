import unittest
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
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


class BaseTestCase(AsyncHTTPTestCase):
    config = TestConfig

    def get_app(self):
        # Create the Tornado application using the Flask-like create_app function
        return create_app(self.config)

    def setUp(self):
        super().setUp()
        self.app_context = self._app_context()
        self.app_context.__enter__()
        db.create_all()
        user = User(username='test', email='test@example.com', password='foo')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.close()
        db.drop_all()
        self.app_context.__exit__(None, None, None)
        super().tearDown()

    def _app_context(self):
        # Tornado does not have an app_context equivalent, so we simulate it
        class AppContext:
            def __init__(self, app):
                self.app = app

            def __enter__(self):
                # Simulate entering the app context
                pass

            def __exit__(self, exc_type, exc_value, traceback):
                # Simulate exiting the app context
                pass

        return AppContext(self._app)
