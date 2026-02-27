from bottle import Bottle, redirect, request
from alchemical.bottle import Alchemical
# from bottle_marshmallow import Marshmallow  # No direct equivalent for Flask-Marshmallow
# from bottle_cors import CORS  # No direct equivalent for Flask-CORS
# from bottle_mail import Mail  # No direct equivalent for Flask-Mail
# from apifairy import APIFairy  # No direct equivalent for Flask-APIFairy
from config import Config

db = Alchemical()
# ma = Marshmallow()
# cors = CORS()
# mail = Mail()
# apifairy = APIFairy()


def create_app(config_class=Config):
    app = Bottle()
    app.config = config_class

    # extensions
    from api import models
    db.init_app(app)
    # ma.init_app(app)
    # if app.config.USE_CORS:  # pragma: no branch
    #     cors.init_app(app)
    # mail.init_app(app)
    # apifairy.init_app(app)

    # blueprints (replaced with direct route imports)
    from api.errors import errors
    errors(app)
    from api.tokens import tokens
    tokens(app)
    from api.users import users
    users(app)
    from api.posts import posts
    posts(app)
    from api.fake import fake
    fake(app)

    # define the shell context (removed as Bottle does not support this natively)
    # @app.shell_context_processor
    # def shell_context():  # pragma: no cover
    #     ctx = {'db': db}
    #     for attr in dir(models):
    #         model = getattr(models, attr)
    #         if hasattr(model, '__bases__') and \
    #                 db.Model in getattr(model, '__bases__'):
    #             ctx[attr] = model
    #     return ctx

    @app.get('/')
    def index():  # pragma: no cover
        return redirect('/docs')  # Hardcoded URL for apifairy.docs

    # After request hook (removed as Bottle does not support this natively)
    # @app.after_request
    # def after_request(response):
    #     # Werkzeug sometimes does not flush the request body so we do it here
    #     request.get_data()
    #     return response

    return app
