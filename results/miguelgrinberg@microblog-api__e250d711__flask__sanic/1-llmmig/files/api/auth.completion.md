### Explanation of Changes

To migrate the code from Flask to Sanic, the following changes were made:

1. **Sanic Imports**: Replaced Flask-specific imports (`flask`, `flask_httpauth`, `werkzeug.exceptions`) with Sanic equivalents. Sanic does not have a direct equivalent for `flask_httpauth`, so custom middleware and decorators were implemented for authentication.

2. **Authentication Middleware**: Sanic does not have built-in support for `HTTPBasicAuth` or `HTTPTokenAuth`. Custom middleware and helper functions were created to handle basic authentication and token authentication.

3. **Error Handling**: Sanic uses exceptions for error handling. Replaced `werkzeug.exceptions` with `sanic.exceptions` and raised appropriate exceptions (`Unauthorized`, `Forbidden`) where necessary.

4. **Sanic Context**: Replaced `current_app` with `app.ctx` to access application-level configurations in Sanic.

5. **Database Access**: Retained the database access logic (`db.session`) as it is assumed to be compatible with Sanic.

Below is the modified code:

---

### Modified Code
```python
from sanic import Sanic, response
from sanic.exceptions import Unauthorized, Forbidden
from functools import wraps

from api.app import db
from api.models import User

app = Sanic.get_app()

# Custom Basic Authentication
def basic_auth_required(handler):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            raise Unauthorized("Authentication required", scheme="Basic")
        
        try:
            auth_decoded = auth_header.split(" ", 1)[1]
            username, password = auth_decoded.encode("ascii").decode("base64").split(":")
        except Exception:
            raise Unauthorized("Invalid authentication credentials", scheme="Basic")
        
        user = await verify_password(username, password)
        if not user:
            raise Unauthorized("Invalid username or password", scheme="Basic")
        
        request.ctx.user = user
        return await handler(request, *args, **kwargs)
    return wrapper

# Custom Token Authentication
def token_auth_required(handler):
    @wraps(handler)
    async def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise Unauthorized("Authentication required", scheme="Bearer")
        
        access_token = auth_header.split(" ", 1)[1]
        user = await verify_token(access_token)
        if not user:
            raise Unauthorized("Invalid or expired token", scheme="Bearer")
        
        request.ctx.user = user
        return await handler(request, *args, **kwargs)
    return wrapper

# Verify Password Function
async def verify_password(username, password):
    if username and password:
        user = db.session.scalar(User.select().filter_by(username=username))
        if user is None:
            user = db.session.scalar(User.select().filter_by(email=username))
        if user and user.verify_password(password):
            return user
    return None

# Verify Token Function
async def verify_token(access_token):
    if app.ctx.config.get('DISABLE_AUTH', False):
        user = db.session.get(User, 1)
        user.ping()
        return user
    if access_token:
        return User.verify_access_token(access_token)
    return None

# Error Handlers
@app.exception(Unauthorized)
async def handle_unauthorized(request, exception):
    return response.json({
        'code': 401,
        'message': 'Unauthorized',
        'description': str(exception),
    }, status=401, headers={'WWW-Authenticate': exception.scheme})

@app.exception(Forbidden)
async def handle_forbidden(request, exception):
    return response.json({
        'code': 403,
        'message': 'Forbidden',
        'description': str(exception),
    }, status=403)
```

---

### Key Notes:
1. **Middleware**: The `basic_auth_required` and `token_auth_required` decorators replace Flask's `@basic_auth.verify_password` and `@token_auth.verify_token` functionality.
2. **Error Handling**: Sanic uses exceptions for error handling, so `Unauthorized` and `Forbidden` exceptions are raised directly.
3. **Sanic Context**: Application-level configurations are accessed using `app.ctx.config`.

This code assumes that the rest of the application is compatible with Sanic and that the database access logic (`db.session`) remains unchanged.