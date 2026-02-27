import cherrypy
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from cherrypy._cperror import HTTPError

class ErrorHandler:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def default(self, *args, **kwargs):
        """Default handler for undefined routes."""
        raise HTTPError(404, "The requested resource was not found.")

    @staticmethod
    def handle_http_error(status, message, traceback, version):
        """Handle HTTP exceptions."""
        return {
            'code': int(status.split(' ')[0]),
            'message': message,
            'description': traceback,
        }

    @staticmethod
    def handle_sqlalchemy_integrity_error(error):
        """Handle SQLAlchemy IntegrityError."""
        cherrypy.response.status = 400
        return {
            'code': 400,
            'message': 'Database integrity error',
            'description': str(error.orig),
        }

    @staticmethod
    def handle_sqlalchemy_error(error):
        """Handle generic SQLAlchemyError."""
        if cherrypy.config.get('debug', False):
            cherrypy.response.status = 500
            return {
                'code': 500,
                'message': 'Database error',
                'description': str(error),
            }
        else:
            cherrypy.response.status = 500
            return {
                'code': 500,
                'message': 'Internal Server Error',
                'description': 'The server encountered an internal error and was unable to complete your request.',
            }

    @staticmethod
    def handle_validation_error(code, messages):
        """Handle validation errors."""
        cherrypy.response.status = code
        return {
            'code': code,
            'message': 'Validation Error',
            'description': ('The server found one or more errors in the '
                            'information that you sent.'),
            'errors': messages,
        }


class API:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {"message": "Welcome to the API"}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def trigger_error(self):
        """Example endpoint to trigger an error."""
        raise IntegrityError("Simulated integrity error", None, None)


# CherryPy Configuration
if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 8080,
        'debug': True,  # Equivalent to Flask's DEBUG config
    })

    # Error Handling
    cherrypy.config.update({
        'error_page.default': ErrorHandler.handle_http_error,
    })

    # Mount the application
    root = API()
    root.errors = ErrorHandler()
    cherrypy.quickstart(root)
