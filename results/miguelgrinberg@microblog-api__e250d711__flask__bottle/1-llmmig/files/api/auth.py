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
