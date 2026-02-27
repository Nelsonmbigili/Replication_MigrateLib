### Explanation of Changes:
To migrate the code from Flask to Tornado, the following changes were made:
1. **HTTP Authentication**: Tornado does not have built-in HTTP authentication like Flask's `HTTPBasicAuth` and `HTTPTokenAuth`. Custom authentication logic was implemented using Tornado's request handlers.
2. **Error Handling**: Flask's `Unauthorized` and `Forbidden` exceptions were replaced with Tornado's HTTP error handling using `tornado.web.HTTPError`.
3. **Request Context**: Tornado does not have a `current_app` equivalent. Configuration values (like `DISABLE_AUTH`) were passed explicitly to the handlers or stored in the application settings.
4. **Database Access**: The database access logic remains the same, assuming `db` and `User` are compatible with Tornado. However, the authentication logic was integrated into Tornado's request handlers.

Below is the modified code:

---

### Modified Code:
```python
from tornado.web import RequestHandler, HTTPError
from api.app import db
from api.models import User


class BaseAuthHandler(RequestHandler):
    def initialize(self, config):
        self.config = config

    def verify_password(self, username, password):
        if username and password:
            user = db.session.scalar(User.select().filter_by(username=username))
            if user is None:
                user = db.session.scalar(User.select().filter_by(email=username))
            if user and user.verify_password(password):
                return user
        return None

    def verify_token(self, access_token):
        if self.config.get('DISABLE_AUTH', False):
            user = db.session.get(User, 1)
            user.ping()
            return user
        if access_token:
            return User.verify_access_token(access_token)
        return None

    def auth_error(self, status=401):
        if status == 403:
            raise HTTPError(403, reason="Forbidden")
        else:
            raise HTTPError(401, reason="Unauthorized")


class BasicAuthHandler(BaseAuthHandler):
    def post(self):
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        user = self.verify_password(username, password)
        if not user:
            self.auth_error(401)
        self.write({
            'message': 'Authentication successful',
            'user_id': user.id
        })


class TokenAuthHandler(BaseAuthHandler):
    def post(self):
        access_token = self.get_argument("access_token", None)
        user = self.verify_token(access_token)
        if not user:
            self.auth_error(401)
        self.write({
            'message': 'Token verification successful',
            'user_id': user.id
        })
```

---

### Key Notes:
1. **Handler Initialization**: Tornado's `initialize` method is used to pass configuration (`config`) to the handlers.
2. **Error Handling**: Tornado's `HTTPError` is used to handle authentication errors (`401 Unauthorized` and `403 Forbidden`).
3. **Request Arguments**: Tornado's `get_argument` method is used to retrieve request parameters (e.g., `username`, `password`, `access_token`).
4. **Routing**: The above handlers need to be added to Tornado's application routing (not shown here, as it is outside the scope of the provided code).

This code assumes that the rest of the application (e.g., database setup, Tornado application initialization) is already configured to work with Tornado.