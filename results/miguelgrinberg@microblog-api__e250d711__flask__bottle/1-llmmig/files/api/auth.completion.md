### Explanation of Changes:
To migrate the code from Flask to Bottle, the following changes were made:
1. Replaced Flask's `HTTPBasicAuth` and `HTTPTokenAuth` with custom implementations since Bottle does not have built-in support for these authentication mechanisms.
2. Removed Flask-specific imports (`current_app`, `HTTPBasicAuth`, `HTTPTokenAuth`) and replaced them with equivalent logic using Bottle's framework.
3. Replaced Flask's `Unauthorized` and `Forbidden` exceptions (from `werkzeug.exceptions`) with custom error responses since Bottle does not provide these exceptions.
4. Adjusted the error handler functions to return responses in a Bottle-compatible format.
5. Removed `current_app` usage and replaced it with a direct configuration dictionary for `DISABLE_AUTH`.

### Modified Code:
```python
from bottle import request, response, HTTPResponse
from api.app import db
from api.models import User

# Configuration dictionary to replace Flask's `current_app.config`
config = {
    'DISABLE_AUTH': False  # Set this to True to disable authentication
}

# Custom Basic Authentication implementation
def verify_password(username, password):
    if username and password:
        user = db.session.scalar(User.select().filter_by(username=username))
        if user is None:
            user = db.session.scalar(User.select().filter_by(email=username))
        if user and user.verify_password(password):
            return user
    return None

def basic_auth_error(status=401):
    error = {
        401: {'code': 401, 'message': 'Unauthorized', 'description': 'Authentication is required.'},
        403: {'code': 403, 'message': 'Forbidden', 'description': 'You do not have permission to access this resource.'}
    }.get(status, {'code': 401, 'message': 'Unauthorized', 'description': 'Authentication is required.'})
    response.status = error['code']
    response.headers['WWW-Authenticate'] = 'Form'
    return error

# Custom Token Authentication implementation
def verify_token(access_token):
    if config['DISABLE_AUTH']:
        user = db.session.get(User, 1)
        user.ping()
        return user
    if access_token:
        return User.verify_access_token(access_token)
    return None

def token_auth_error(status=401):
    error = {
        401: {'code': 401, 'message': 'Unauthorized', 'description': 'Authentication is required.'},
        403: {'code': 403, 'message': 'Forbidden', 'description': 'You do not have permission to access this resource.'}
    }.get(status, {'code': 401, 'message': 'Unauthorized', 'description': 'Authentication is required.'})
    response.status = error['code']
    return error
```

### Key Notes:
- The `verify_password` and `verify_token` functions remain largely unchanged, except for the removal of Flask-specific components.
- The `basic_auth_error` and `token_auth_error` functions now use Bottle's `response` object to set the status code and headers.
- A `config` dictionary is used to replace Flask's `current_app.config` for configuration management.
- The `HTTPResponse` class from Bottle is not explicitly used here, but it can be utilized if more complex response handling is required.