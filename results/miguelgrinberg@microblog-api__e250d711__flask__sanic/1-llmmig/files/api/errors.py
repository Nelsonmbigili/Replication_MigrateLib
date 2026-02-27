from sanic import Blueprint, Sanic, response
from sanic.exceptions import SanicException, InternalServerError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.app import apifairy

errors = Blueprint('errors', url_prefix='/errors')


@errors.exception(SanicException)
async def http_error(request, exception):
    return response.json({
        'code': exception.status_code,
        'message': exception.args[0] if exception.args else 'HTTP Error',
        'description': getattr(exception, 'description', ''),
    }, status=exception.status_code)


@errors.exception(IntegrityError)
async def sqlalchemy_integrity_error(request, exception):  # pragma: no cover
    return response.json({
        'code': 400,
        'message': 'Database integrity error',
        'description': str(exception.orig),
    }, status=400)


@errors.exception(SQLAlchemyError)
async def sqlalchemy_error(request, exception):  # pragma: no cover
    if request.app.config.get('DEBUG', False):
        return response.json({
            'code': InternalServerError.status_code,
            'message': 'Database error',
            'description': str(exception),
        }, status=500)
    else:
        return response.json({
            'code': InternalServerError.status_code,
            'message': InternalServerError().args[0],
            'description': InternalServerError.description,
        }, status=500)


@apifairy.error_handler
async def validation_error(request, code, messages):  # pragma: no cover
    return response.json({
        'code': code,
        'message': 'Validation Error',
        'description': ('The server found one or more errors in the '
                        'information that you sent.'),
        'errors': messages,
    }, status=code)
