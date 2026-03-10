import cherrypy
from werkzeug.exceptions import Unauthorized, Forbidden

from api.app import db
from api.models import User


class Auth:
    @cherrypy.tools.json_out()
    def verify_password(self, username, password):
        if username and password:
            user = db.session.scalar(User.select().filter_by(username=username))
            if user is None:
                user = db.session.scalar(User.select().filter_by(email=username))
            if user and user.verify_password(password):
                return user

    @cherrypy.tools.json_out()
    def basic_auth_error(self, status=401):
        error = (Forbidden if status == 403 else Unauthorized)()
        return {
            'code': error.code,
            'message': error.name,
            'description': error.description,
        }, error.code, {'WWW-Authenticate': 'Form'}

    @cherrypy.tools.json_out()
    def verify_token(self, access_token):
        if cherrypy.config.get('DISABLE_AUTH', False):
            user = db.session.get(User, 1)
            user.ping()
            return user
        if access_token:
            return User.verify_access_token(access_token)

    @cherrypy.tools.json_out()
    def token_auth_error(self, status=401):
        error = (Forbidden if status == 403 else Unauthorized)()
        return {
            'code': error.code,
            'message': error.name,
            'description': error.description,
        }, error.code


auth = Auth()
