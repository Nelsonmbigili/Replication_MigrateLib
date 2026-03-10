from bottle import error
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.app import apifairy

@error(HTTPException)
def http_error(error):
    return {
        'code': error.status_code,
        'message': error.body,
        'description': error.description,
    }, error.status_code


@error(IntegrityError)
def sqlalchemy_integrity_error(error):  # pragma: no cover
    return {
        'code': 400,
        'message': 'Database integrity error',
        'description': str(error.orig),
    }, 400


@error(SQLAlchemyError)
def sqlalchemy_error(error):  # pragma: no cover
    if True:  # Replace with actual debug check if needed
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
