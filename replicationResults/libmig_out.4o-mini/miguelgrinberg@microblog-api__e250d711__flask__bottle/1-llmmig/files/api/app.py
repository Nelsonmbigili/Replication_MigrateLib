from bottle import Bottle, redirect, request
from alchemical.bottle import Alchemical
from marshmallow import Marshmallow
from config import Config

db = Alchemical()
ma = Marshmallow()
mail = None  # Bottle does not have a built-in mail extension
apifairy = None  # Bottle does not have a built-in API fairy extension

def create_app(config_class=Config):
    app = Bottle()
    # Configuration is not directly supported in Bottle like Flask
    # You may need to handle configuration differently

    # extensions
    from api import models
    db.init_app(app)
    ma.init_app(app)
    # CORS handling is not included as Bottle does not have built-in support
    # mail.init_app(app)  # Not applicable in Bottle
    # apifairy.init_app(app)  # Not applicable in Bottle

    # blueprints
    from api.errors import errors
    app.mount('/errors', errors)
    from api.tokens import tokens
    app.mount('/api/tokens', tokens)
    from api.users import users
    app.mount('/api/users', users)
    from api.posts import posts
    app.mount('/api/posts', posts)
    from api.fake import fake
    app.mount('/fake', fake)

    @app.route('/')
    def index():  # pragma: no cover
        return redirect('/api/docs')  # Adjusted to a direct URL since Bottle does not have url_for

    @app.hook('after_request')
    def after_request():
        # Bottle does not have a direct equivalent to Werkzeug's request.get_data()
        pass

    return app
