### Explanation of Changes

To migrate the code from using the Flask framework to the Sanic framework, the following changes were made:

1. **Import Statements**: The import statements were updated to use Sanic's equivalent modules. Sanic does not have a direct equivalent for `flask_httpauth`, so we will need to implement basic and token authentication manually or use a different approach.
  
2. **Context Management**: The `current_app` context from Flask is not available in Sanic. Instead, we can directly access the application instance.

3. **Error Handling**: The error handling mechanism was adjusted to fit Sanic's response structure.

4. **Session Management**: Sanic does not use the same session management as Flask, so we need to ensure that the database session is handled appropriately.

5. **Decorator Changes**: The decorators for authentication need to be adapted to Sanic's request handling.

Here is the modified code:

```python
from sanic import Sanic
from sanic.response import json
from sanic.exceptions import Unauthorized, Forbidden

from api.app import db
from api.models import User

app = Sanic("MyApp")

@app.middleware('request')
async def verify_password(request):
    username = request.headers.get('Authorization')
    password = request.headers.get('Password')
    if username and password:
        user = await db.session.scalar(User.select().filter_by(username=username))
        if user is None:
            user = await db.session.scalar(User.select().filter_by(email=username))
        if user and user.verify_password(password):
            request.user = user
            return

    raise Unauthorized("Invalid credentials")

@app.exception(Unauthorized)
async def basic_auth_error(request, exception):
    return json({
        'code': 401,
        'message': 'Unauthorized',
        'description': str(exception),
    }, status=401)

@app.middleware('request')
async def verify_token(request):
    access_token = request.headers.get('Authorization')
    if app.config['DISABLE_AUTH']:
        user = await db.session.get(User, 1)
        user.ping()
        request.user = user
        return
    if access_token:
        user = await User.verify_access_token(access_token)
        if user:
            request.user = user
            return

    raise Unauthorized("Invalid token")

@app.exception(Unauthorized)
async def token_auth_error(request, exception):
    return json({
        'code': 401,
        'message': 'Unauthorized',
        'description': str(exception),
    }, status=401)
```

### Notes:
- The authentication logic is now implemented as middleware functions in Sanic.
- The error handling is done using Sanic's exception handling mechanism.
- The database session handling is assumed to be asynchronous, which is typical in Sanic applications. Adjustments may be needed based on the actual implementation of the `db` object.