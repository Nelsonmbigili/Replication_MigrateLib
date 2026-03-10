from bottle import response, request
from api.app import db
from api.models import User

def verify_password(username, password):
    if username and password:
        user = db.session.scalar(User.select().filter_by(username=username))
        if user is None:
            user = db.session.scalar(User.select().filter_by(email=username))
        if user and user.verify_password(password):
            return user

def basic_auth_error(status=401):
    error = (403 if status == 403 else 401)
    response.status = error
    return {
        'code': error,
        'message': 'Unauthorized' if error == 401 else 'Forbidden',
        'description': 'Access denied' if error == 401 else 'Forbidden access',
    }

@basic_auth.error_handler
def basic_auth_error(status=401):
    error = (Forbidden if status == 403 else Unauthorized)()
    return {
        'code': error.code,
        'message': error.name,
        'description': error.description,
    }, error.code, {'WWW-Authenticate': 'Form'}


@token_auth.verify_token
def verify_token(access_token):
    if request.app.config['DISABLE_AUTH']:
        user = db.session.get(User, 1)
        user.ping()
        return user
    if access_token:
        return User.verify_access_token(access_token)

def token_auth_error(status=401):
    error = (403 if status == 403 else 401)
    response.status = error
    return {
        'code': error,
        'message': 'Unauthorized' if error == 401 else 'Forbidden',
        'description': 'Access denied' if error == 401 else 'Forbidden access',
    }