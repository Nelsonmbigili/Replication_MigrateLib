import unittest
import cherrypy
from api.app import db
from api.models import User
from config import Config


class TestConfig(Config):
    SERVER_NAME = 'localhost:8080'  # Changed port to 8080 for CherryPy
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
        cherrypy.tree.mount(self.create_app(self.config))
        self.app_context = cherrypy.request
        db.create_all()
        user = User(username='test', email='test@example.com', password='foo')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.close()
        db.drop_all()
        cherrypy.tree.apps.clear()

    def create_app(self, config):
        # This method should return a CherryPy application instance
        # The implementation of this method is assumed to be defined elsewhere
        pass
