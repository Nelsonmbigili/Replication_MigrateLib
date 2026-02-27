import json
from tornado.web import RequestHandler, HTTPError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from tornado.escape import json_encode

class BaseHandler(RequestHandler):
    def write_error(self, status_code, **kwargs):
        """Custom error handler for Tornado."""
        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]
            if isinstance(exception, HTTPError):
                self.set_status(status_code)
                self.write({
                    'code': status_code,
                    'message': exception.log_message or 'HTTP Error',
                    'description': self._reason,
                })
            elif isinstance(exception, IntegrityError):
                self.set_status(400)
                self.write({
                    'code': 400,
                    'message': 'Database integrity error',
                    'description': str(exception.orig),
                })
            elif isinstance(exception, SQLAlchemyError):
                debug = self.application.settings.get('debug', False)
                if debug:
                    self.set_status(500)
                    self.write({
                        'code': 500,
                        'message': 'Database error',
                        'description': str(exception),
                    })
                else:
                    self.set_status(500)
                    self.write({
                        'code': 500,
                        'message': 'Internal Server Error',
                        'description': 'The server encountered an internal error and was unable to complete your request.',
                    })
            else:
                # Generic error handling
                self.set_status(status_code)
                self.write({
                    'code': status_code,
                    'message': 'Unknown Error',
                    'description': 'An unknown error occurred.',
                })
        else:
            # Default error response
            self.set_status(status_code)
            self.write({
                'code': status_code,
                'message': 'Error',
                'description': 'An error occurred.',
            })

class ValidationErrorHandler(BaseHandler):
    def validation_error(self, code, messages):
        """Custom validation error handler."""
        self.set_status(code)
        self.write({
            'code': code,
            'message': 'Validation Error',
            'description': ('The server found one or more errors in the '
                            'information that you sent.'),
            'errors': messages,
        })

# Example usage in an application
class ExampleHandler(BaseHandler):
    def get(self):
        # Simulate an error for demonstration
        raise HTTPError(404, reason="Resource not found")

# Tornado application setup
def make_app():
    return tornado.web.Application([
        (r"/example", ExampleHandler),
    ], debug=True)  # Pass debug=True for development mode
