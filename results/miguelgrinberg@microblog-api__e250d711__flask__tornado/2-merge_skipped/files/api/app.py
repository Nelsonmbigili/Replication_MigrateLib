import tornado.ioloop
import tornado.web
from alchemical.tornado import Alchemical  # Assuming Tornado-compatible Alchemical
from marshmallow import Schema  # Tornado does not have a direct Marshmallow integration
from tornado_cors import CorsMixin  # Tornado-compatible CORS library
from tornado_mailer import Mailer  # Tornado-compatible Mail library
from apifairy import APIFairy  # Assuming APIFairy is compatible with Tornado
from config import Config

db = Alchemical()
ma = Schema()  # Marshmallow schema initialization
mail = Mailer()
apifairy = APIFairy()


class BaseHandler(tornado.web.RequestHandler):
    """Base handler to include shared functionality."""
    def set_default_headers(self):
        if self.application.settings.get('USE_CORS', False):
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def options(self):
        # Handle CORS preflight requests
        self.set_status(204)
        self.finish()

    # blueprints
    from api.errors import errors
    app.register_blueprint(errors)
    from api.tokens import tokens
    app.register_blueprint(tokens, url_prefix='/api')
    from api.users import users
    app.register_blueprint(users, url_prefix='/api')
    from api.posts import posts
    app.register_blueprint(posts, url_prefix='/api')
    from api.fake import fake
    app.register_blueprint(fake)

class IndexHandler(BaseHandler):
    """Handler for the index route."""
    def get(self):
        self.redirect('/docs')  # Redirect to API documentation


class AfterRequestHandler(BaseHandler):
    """Handler to simulate after_request functionality."""
    def prepare(self):
        # Tornado automatically handles request body flushing, so no action is needed here
        pass


def make_app(config_class=Config):
    # Load configuration
    config = config_class()

    # Initialize extensions
    db.init_app(config)
    mail.init_app(config)
    apifairy.init_app(config)

    # Define routes
    from api.errors import ErrorsHandler
    from api.tokens import TokensHandler
    from api.users import UsersHandler
    from api.posts import PostsHandler
    from api.fake import FakeHandler

    routes = [
        (r"/", IndexHandler),
        (r"/api/errors", ErrorsHandler),
        (r"/api/tokens", TokensHandler),
        (r"/api/users", UsersHandler),
        (r"/api/posts", PostsHandler),
        (r"/api/fake", FakeHandler),
    ]

    # Create Tornado application
    return tornado.web.Application(
        routes,
        debug=config.DEBUG,
        USE_CORS=config.USE_CORS,
        db=db,
        mail=mail,
        apifairy=apifairy,
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8000)  # Default port
    tornado.ioloop.IOLoop.current().start()