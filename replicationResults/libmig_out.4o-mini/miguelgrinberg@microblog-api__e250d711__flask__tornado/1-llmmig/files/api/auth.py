from tornado.web import HTTPError
from api.app import db
from api.models import User

class AuthHandler:
    @staticmethod
    def verify_password(username, password):
        if username and password:
            user = db.session.scalar(User.select().filter_by(username=username))
            if user is None:
                user = db.session.scalar(User.select().filter_by(email=username))
            if user and user.verify_password(password):
                return user

    @staticmethod
    def basic_auth_error(status=401):
        error = HTTPError(status)
        return {
            'code': error.status_code,
            'message': error.reason,
            'description': error.log_message,
        }, error.status_code

    @staticmethod
    def verify_token(access_token):
        if db.session.get(User, 1):  # Assuming this is a way to get a default user
            user = db.session.get(User, 1)
            user.ping()
            return user
        if access_token:
            return User.verify_access_token(access_token)

    @staticmethod
    def token_auth_error(status=401):
        error = HTTPError(status)
        return {
            'code': error.status_code,
            'message': error.reason,
            'description': error.log_message,
        }, error.status_code
