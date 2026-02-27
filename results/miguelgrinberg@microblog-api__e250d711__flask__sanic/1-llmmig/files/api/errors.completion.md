### Explanation of Changes

To migrate the code from Flask to Sanic, the following changes were made:

1. **Blueprint Replacement**: In Sanic, `Blueprint` is replaced with `Blueprint` from `sanic`. The syntax for registering error handlers is also different.
2. **Error Handling**: Sanic uses `@blueprint.exception` to handle exceptions instead of `@errors.app_errorhandler`.
3. **Accessing App Configuration**: In Sanic, app configuration is accessed via `request.app.config` instead of `current_app.config`.
4. **HTTPException Handling**: Sanic's `SanicException` is used for HTTP exceptions.
5. **Response Format**: Sanic uses `json` to return JSON responses.
6. **Error Handler for Validation**: The `apifairy.error_handler` decorator is replaced with a custom error handler in Sanic.

Below is the modified code:

---

### Modified Code
```python
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
```

---

### Key Notes:
- The `response.json` method is used to return JSON responses in Sanic.
- The `request` object is passed to all exception handlers in Sanic, allowing access to app configuration and other request-specific data.
- The `@apifairy.error_handler` decorator remains unchanged, assuming `apifairy` is compatible with Sanic. If not, it may require further adjustments.