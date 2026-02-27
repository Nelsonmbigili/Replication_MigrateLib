### Explanation of Changes
To migrate the given code from Flask to FastAPI, the following changes were made:
1. **Blueprint to FastAPI Router**: Flask's `Blueprint` was replaced with FastAPI's `APIRouter`.
2. **Error Handlers**: Flask's `@app_errorhandler` was replaced with FastAPI's `@app.exception_handler` for handling exceptions.
3. **HTTPException Handling**: FastAPI's `HTTPException` was used directly, and the response structure was adjusted to match FastAPI's exception handling.
4. **Dependency on `current_app`**: Flask's `current_app` was replaced with FastAPI's `app.state` for accessing application-level configuration.
5. **Validation Error Handling**: FastAPI's validation errors are handled differently, so the `validation_error` function was adapted to use FastAPI's exception handling mechanism.

### Modified Code
```python
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from api.app import apifairy

errors = APIRouter()


@errors.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'code': exc.status_code,
            'message': exc.detail,
            'description': exc.detail,
        },
    )


@errors.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error(request: Request, exc: IntegrityError):  # pragma: no cover
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={
            'code': HTTP_400_BAD_REQUEST,
            'message': 'Database integrity error',
            'description': str(exc.orig),
        },
    )


@errors.exception_handler(SQLAlchemyError)
async def sqlalchemy_error(request: Request, exc: SQLAlchemyError):  # pragma: no cover
    app: FastAPI = request.app
    if app.state.config.get('DEBUG', False):
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'code': HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Database error',
                'description': str(exc),
            },
        )
    else:
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                'code': HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Internal Server Error',
                'description': 'The server encountered an internal error and was unable to complete your request.',
            },
        )


@apifairy.error_handler
async def validation_error(code, messages):  # pragma: no cover
    return JSONResponse(
        status_code=code,
        content={
            'code': code,
            'message': 'Validation Error',
            'description': ('The server found one or more errors in the '
                            'information that you sent.'),
            'errors': messages,
        },
    )
```

### Key Notes
- The `FastAPI` application should include the `errors` router using `app.include_router(errors)`.
- The `app.state.config` is used to mimic Flask's `current_app.config`. Ensure that the `config` dictionary is set in the `FastAPI` app's state during initialization.
- The `apifairy.error_handler` decorator is assumed to work similarly in FastAPI, as no specific details about its implementation were provided.