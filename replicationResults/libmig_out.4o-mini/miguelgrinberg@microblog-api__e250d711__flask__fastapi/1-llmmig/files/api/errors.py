from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi.responses import JSONResponse

from api.app import apifairy

app = FastAPI()

@app.exception_handler(HTTPException)
async def http_error(request, error: HTTPException):
    return JSONResponse(
        status_code=error.status_code,
        content={
            'code': error.status_code,
            'message': error.detail,
            'description': error.detail,
        },
    )

@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error(request, error: IntegrityError):  # pragma: no cover
    return JSONResponse(
        status_code=400,
        content={
            'code': 400,
            'message': 'Database integrity error',
            'description': str(error.orig),
        },
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error(request, error: SQLAlchemyError):  # pragma: no cover
    if app.debug:  # Accessing debug mode directly from the app instance
        return JSONResponse(
            status_code=500,
            content={
                'code': 500,
                'message': 'Database error',
                'description': str(error),
            },
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                'code': 500,
                'message': 'Internal Server Error',
                'description': 'An internal server error occurred.',
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
