from sanic import Sanic, response
from sanic_cors import CORS
from alchemical.sanic import Alchemical
from sanic_marshmallow import Marshmallow
from sanic_mail import Mail
from apifairy import APIFairy
from config import Config

db = Alchemical()
ma = Marshmallow()
cors = CORS()
mail = Mail()
apifairy = APIFairy()


def create_app(config_class=Config):
    app = Sanic(__name__)
    app.config.from_object(config_class)

    # extensions
    from api import models
    db.init_app(app)
    ma.init_app(app)
    if app.config['USE_CORS']:  # pragma: no branch
        cors.init_app(app)
    mail.init_app(app)
    apifairy.init_app(app)

    # blueprints
    from api.errors import errors
    app.blueprint(errors)
    from api.tokens import tokens
    app.blueprint(tokens, url_prefix='/api')
    from api.users import users
    app.blueprint(users, url_prefix='/api')
    from api.posts import posts
    app.blueprint(posts, url_prefix='/api')
    from api.fake import fake
    app.blueprint(fake)

    @app.route('/')
    async def index(request):  # pragma: no cover
        return response.redirect(app.url_for('apifairy.docs'))

    @app.middleware('response')
    async def after_request(request, response):
        # Sanic handles request body differently, but we can still ensure it's read
        await request.json()
        return response

    return app
