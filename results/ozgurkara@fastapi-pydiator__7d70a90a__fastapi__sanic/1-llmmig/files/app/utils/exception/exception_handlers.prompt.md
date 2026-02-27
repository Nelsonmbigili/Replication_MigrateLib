The following Python code currently uses the library "fastapi" version 0.109.1.
Migrate this code to use the library "sanic" version 25.3.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "fastapi" to "sanic".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "fastapi" and "sanic".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import traceback
from typing import Optional, List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from app.utils.error.error_models import ErrorInfoModel
from app.utils.error.error_response import ErrorResponseModel, ErrorInfoContainer
from app.utils.exception.exception_types import DataException, ServiceException


class ExceptionHandlers:

    @staticmethod
    def unhandled_exception(request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ExceptionHandlers.__get_error_content(
                error_info=ErrorInfoContainer.unhandled_error,
                error_detail=[ExceptionHandlers.__get_stack_trace(exc)]
            ),
        )

    @staticmethod
    def data_exception(request, exc: DataException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ExceptionHandlers.__get_error_content(
                error_info=exc.error_info
            ),
        )

    @staticmethod
    def service_exception(request, exc: ServiceException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ExceptionHandlers.__get_error_content(
                error_info=exc.error_info
            ),
        )

    @staticmethod
    def http_exception(request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ExceptionHandlers.__get_error_content(
                error_info=ErrorInfoContainer.unhandled_error,
                error_detail=[exc.detail]
            ),
        )

    @staticmethod
    def validation_exception(request, exc):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ExceptionHandlers.__get_error_content(
                error_info=ErrorInfoContainer.model_validation_error,
                error_detail=exc.errors()
            ),
        )

    @staticmethod
    def __get_error_content(error_info: ErrorInfoModel, error_detail: Optional[List] = None):
        return jsonable_encoder(
            ErrorResponseModel(
                error_code=error_info.code,
                error_message=error_info.message,
                error_detail=error_detail,
            ).dict()
        )

    @staticmethod
    def __get_stack_trace(exc: Exception) -> str:
        return "".join(traceback.TracebackException.from_exception(exc).format())

```