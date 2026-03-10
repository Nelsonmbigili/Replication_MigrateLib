from tornado.web import Application, RequestHandler
from alchemical.tornado import Alchemical
from marshmallow import Schema  # Tornado does not have a direct equivalent for Flask-Marshmallow
from tornado_cors import CorsMiddleware  # Assuming a CORS middleware for Tornado
from config import Config

db = Alchemical()

class IndexHandler(RequestHandler):
    def get(self):
        self.redirect('/docs')  # Assuming '/docs' is the equivalent of 'apifairy.docs'

def create_app(config_class=Config):
    app = Application([
        (r"/", IndexHandler),
        # Add other routes here, e.g., (r"/api/tokens", TokensHandler),
    ])

    app.settings.update({
        'config': config_class,
    })

    # extensions
    from api import models
    db.init_app(app)

    # CORS
    if app.settings['config'].USE_CORS:  # pragma: no branch
        app.add_middleware(CorsMiddleware)

    # Define other handlers and routes here
    from api.errors import ErrorsHandler
    app.add_handlers(r".*", [(r"/api/errors", ErrorsHandler)])

    from api.tokens import TokensHandler
    app.add_handlers(r".*", [(r"/api/tokens", TokensHandler)])

    from api.users import UsersHandler
    app.add_handlers(r".*", [(r"/api/users", UsersHandler)])

    from api.posts import PostsHandler
    app.add_handlers(r".*", [(r"/api/posts", PostsHandler)])

    from api.fake import FakeHandler
    app.add_handlers(r".*", [(r"/api/fake", FakeHandler)])

    return app
