import cherrypy
from alchemical.cherrypy import Alchemical
from marshmallow import Marshmallow
from cherrypy_cors import CORS
from cherrypy_mail import Mail
from apifairy import APIFairy
from config import Config

db = Alchemical()
ma = Marshmallow()
cors = CORS()
mail = Mail()
apifairy = APIFairy()


def create_app(config_class=Config):
    cherrypy.config.update(config_class)

    # extensions
    from api import models
    db.init_app(cherrypy)
    ma.init_app(cherrypy)
    if cherrypy.config.get('USE_CORS', False):  # pragma: no branch
        cors.init_app(cherrypy)
    mail.init_app(cherrypy)
    apifairy.init_app(cherrypy)

    # blueprints
    from api.errors import errors
    cherrypy.tree.mount(errors, '/errors')
    from api.tokens import tokens
    cherrypy.tree.mount(tokens, '/api/tokens')
    from api.users import users
    cherrypy.tree.mount(users, '/api/users')
    from api.posts import posts
    cherrypy.tree.mount(posts, '/api/posts')
    from api.fake import fake
    cherrypy.tree.mount(fake, '/fake')

    @cherrypy.expose
    def index():  # pragma: no cover
        raise cherrypy.HTTPRedirect(apifairy.docs)

    @cherrypy.tools.register('after_handler')
    def after_request():
        # CherryPy automatically handles request body flushing
        pass

    return cherrypy
