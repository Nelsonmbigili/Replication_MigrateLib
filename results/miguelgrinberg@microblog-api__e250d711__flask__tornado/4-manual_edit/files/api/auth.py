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
