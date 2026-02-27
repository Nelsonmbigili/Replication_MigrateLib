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
