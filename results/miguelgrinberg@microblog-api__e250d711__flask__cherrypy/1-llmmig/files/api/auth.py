import cherrypy
from cherrypy.lib import auth_basic
from api.app import db
from api.models import User
import json


def verify_password(username, password):
    if username and password:
        user = db.session.scalar(User.select().filter_by(username=username))
        if user is None:
            user = db.session.scalar(User.select().filter_by(email=username))
        if user and user.verify_password(password):
            cherrypy.request.login = user
            return True
    return False


def verify_token(access_token):
    if cherrypy.config.get('DISABLE_AUTH', False):
        user = db.session.get(User, 1)
        user.ping()
        cherrypy.request.login = user
        return True
    if access_token:
        user = User.verify_access_token(access_token)
        if user:
            cherrypy.request.login = user
            return True
    return False


def basic_auth_error():
    raise cherrypy.HTTPError(401, "Unauthorized")


def token_auth_error():
    raise cherrypy.HTTPError(401, "Unauthorized")


class AuthHandler:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def basic_auth(self, username=None, password=None):
        if not verify_password(username, password):
            basic_auth_error()
        return {"message": "Authentication successful"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def token_auth(self, access_token=None):
        if not verify_token(access_token):
            token_auth_error()
        return {"message": "Token authentication successful"}


# CherryPy Configuration
config = {
    '/': {
        'tools.sessions.on': True,
        'tools.auth_basic.on': False,  # Custom authentication logic is used
    }
}

if __name__ == '__main__':
    cherrypy.quickstart(AuthHandler(), '/', config)
