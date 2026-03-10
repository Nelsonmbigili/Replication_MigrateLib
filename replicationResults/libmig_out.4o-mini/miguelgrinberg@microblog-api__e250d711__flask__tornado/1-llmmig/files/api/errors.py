from tornado.web import RequestHandler, HTTPError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.app import apifairy

class ErrorHandler(RequestHandler):

    def http_error(self, error):
        self.set_status(error.code)
        self.write({
            'code': error.code,
            'message': error.name,
            'description': error.description,
        })

    def sqlalchemy_integrity_error(self, error):  # pragma: no cover
        self.set_status(400)
        self.write({
            'code': 400,
            'message': 'Database integrity error',
            'description': str(error.orig),
        })

    def sqlalchemy_error(self, error):  # pragma: no cover
        if self.application.settings['DEBUG'] is True:
            self.set_status(500)
            self.write({
                'code': 500,
                'message': 'Database error',
                'description': str(error),
            })
        else:
            self.set_status(500)
            self.write({
                'code': 500,
                'message': 'Internal Server Error',
                'description': 'An internal server error occurred.',
            })

@apifairy.error_handler
def validation_error(code, messages):  # pragma: no cover
    return {
        'code': code,
        'message': 'Validation Error',
        'description': ('The server found one or more errors in the '
                        'information that you sent.'),
        'errors': messages,
    }, code
