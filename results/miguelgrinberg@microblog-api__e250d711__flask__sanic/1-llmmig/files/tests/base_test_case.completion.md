### Explanation of Changes:
To migrate the code from Flask to Sanic, the following changes were made:
1. **Application Creation**: Flask's `create_app` function was replaced with a Sanic app instance. Sanic does not use `app_context` like Flask, so this was removed.
2. **Database Initialization**: Sanic does not have a built-in `app_context`. Instead, database setup and teardown were handled directly in the `setUp` and `tearDown` methods.
3. **Test Client**: Sanic provides an asynchronous test client. The `self.client` was updated to use Sanic's `app.test_client`.
4. **Asynchronous Support**: Sanic is asynchronous, so the `setUp` and `tearDown` methods were updated to use `async def` and `await` where necessary.
5. **Configuration**: Sanic does not use Flask's `Config` object. Instead, configuration values were set directly on the Sanic app instance.

Below is the modified code:

---

### Modified Code:
```python
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
```

---

### Key Notes:
1. **Sanic's `IsolatedAsyncioTestCase`**: Since Sanic is asynchronous, the test case class was updated to `unittest.IsolatedAsyncioTestCase` to support async methods.
2. **Database Context**: Sanic does not have a direct equivalent to Flask's `app_context`. Instead, database operations were wrapped in `async with` blocks using the app's context.
3. **Test Client**: Sanic's `app.test_client` was used for testing, and it requires asynchronous usage.
4. **Configuration**: Configuration values were directly updated on the Sanic app instance using `self.app.config.update`.

This code assumes that the `create_app` function in `api.app` has been updated to return a Sanic app instance. If `create_app` still returns a Flask app, additional changes would be required in the `create_app` function itself.