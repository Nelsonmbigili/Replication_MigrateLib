import unittest
from api.app import create_app, db
from api.models import User
from config import Config
from sanic import Sanic


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


class BaseTestCase(unittest.IsolatedAsyncioTestCase):
    config = TestConfig

    async def asyncSetUp(self):
        self.app = create_app(self.config)
        self.app.config.update(self.config.__dict__)
        self.client = self.app.test_client
        async with self.app.asgi_client as client:
            self.client = client

        # Initialize the database
        async with self.app.ctx.db.begin() as conn:
            await conn.run_sync(db.create_all)

        # Add a test user
        async with self.app.ctx.db.begin() as conn:
            user = User(username='test', email='test@example.com', password='foo')
            conn.add(user)
            await conn.commit()

    async def asyncTearDown(self):
        # Drop all tables
        async with self.app.ctx.db.begin() as conn:
            await conn.run_sync(db.drop_all)
