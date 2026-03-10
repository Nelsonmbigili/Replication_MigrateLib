### Explanation of Changes

To migrate the provided code from using the Flask framework to the Tornado framework, several key changes were made:

1. **Import Statements**: The `flask` imports were replaced with `tornado` equivalents. Tornado does not have a direct equivalent for `create_app`, so the application setup will be handled differently.
  
2. **Application Context**: Tornado does not use the concept of application contexts like Flask. Therefore, the context management code (`app_context`) was removed.

3. **Test Client**: Tornado does not have a built-in test client like Flask. Instead, we will use `tornado.testing.AsyncHTTPTestCase` to create a test case that can handle asynchronous requests.

4. **Database Setup**: The database setup and teardown logic remains similar, but it is now integrated into the Tornado testing framework.

5. **Asynchronous Testing**: Tornado's testing framework is asynchronous, so the test methods need to be defined as `async` functions.

Here is the modified code:

```python
import unittest
from tornado.testing import AsyncHTTPTestCase
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
        return create_app(self.config)

    async def setUp(self):
        await super().setUp()
        db.create_all()
        user = User(username='test', email='test@example.com', password='foo')
        db.session.add(user)
        db.session.commit()

    async def tearDown(self):
        db.session.close()
        db.drop_all()
        await super().tearDown()
```

### Summary of Changes
- The test class now inherits from `AsyncHTTPTestCase` instead of `unittest.TestCase`.
- The `get_app` method is used to return the Tornado application instance.
- The `setUp` and `tearDown` methods are now asynchronous to accommodate Tornado's testing framework.