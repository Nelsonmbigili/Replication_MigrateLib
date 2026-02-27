from sanic import Sanic, response
from sanic.response import redirect
from sanic_ext import Extend
from alchemical.sanic import Alchemical
from flask_marshmallow import Marshmallow  # Assuming compatibility with Sanic
from sanic_cors import CORS
from flask_mail import Mail  # Assuming compatibility with Sanic
from apifairy import APIFairy  # Assuming compatibility with Sanic
from config import Config

db = Alchemical()
ma = Marshmallow()
cors = CORS()
mail = Mail()
apifairy = APIFairy()


def create_app(config_class=Config):
    app = Sanic("MyApp")
    app.config.update(config_class.__dict__)

    # extensions
    from api import models
    db.init_app(app)
    ma.init_app(app)
    if app.config.get('USE_CORS'):  # pragma: no branch
        Extend(app)  # Enables CORS and other extensions
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

    # define the shell context
    # NOTE: Sanic does not have a direct equivalent for shell context processors.
    # This functionality is omitted.

    @app.get("/")
    async def index(request):  # pragma: no cover
        return redirect(app.url_for('apifairy.docs'))

    @app.middleware("response")
    async def after_request(request, response):
        # Werkzeug sometimes does not flush the request body so we do it here
        request.body  # Accessing the request body to ensure it is flushed
        return response

    return app
