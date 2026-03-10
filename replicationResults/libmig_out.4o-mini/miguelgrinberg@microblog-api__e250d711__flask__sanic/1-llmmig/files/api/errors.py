from sanic import Blueprint
from sanic.exceptions import SanicException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.app import apifairy

errors = Blueprint('errors')


@errors.exception(SanicException)
def http_error(request, error):
    return {
        'code': error.status_code,
        'message': error.name,
        'description': error.args[0],
    }, error.status_code


@errors.exception(IntegrityError)
def sqlalchemy_integrity_error(request, error):  # pragma: no cover
    return {
        'code': 400,
        'message': 'Database integrity error',
        'description': str(error.orig),
    }, 400


@errors.exception(SQLAlchemyError)
def sqlalchemy_error(request, error):  # pragma: no cover
    if request.app.config['DEBUG'] is True:
        return {
            'code': 500,
            'message': 'Database error',
            'description': str(error),
        }, 500
    else:
        return {
            'code': 500,
            'message': 'Internal Server Error',
            'description': 'An internal server error occurred.',
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
