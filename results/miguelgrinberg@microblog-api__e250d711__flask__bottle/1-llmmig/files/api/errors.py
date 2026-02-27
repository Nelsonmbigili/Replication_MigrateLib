from bottle import Bottle, error, request, response
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException, InternalServerError

from api.app import apifairy

app = Bottle()

# Error Handlers
@app.error(HTTPException.code)
def http_error(error):
    return {
        'code': error.status_code,
        'message': error.status_line,
        'description': error.body,
    }, error.status_code


@app.error(400)
def sqlalchemy_integrity_error(error):  # pragma: no cover
    if isinstance(error.exception, IntegrityError):
        return {
            'code': 400,
            'message': 'Database integrity error',
            'description': str(error.exception.orig),
        }, 400


@app.error(500)
def sqlalchemy_error(error):  # pragma: no cover
    if isinstance(error.exception, SQLAlchemyError):
        if app.config.get('DEBUG', False):
            return {
                'code': InternalServerError.code,
                'message': 'Database error',
                'description': str(error.exception),
            }, 500
        else:
            return {
                'code': InternalServerError.code,
                'message': InternalServerError().name,
                'description': InternalServerError.description,
            }, 500


@apifairy.error_handler
def validation_error(code, messages):  # pragma: no cover
    return {
        'code': code,
        'message': 'Validation Error',
        'description': ('The server found one or more errors in the '
                        'information that you sent.'),
        'errors': messages,
    }, code
