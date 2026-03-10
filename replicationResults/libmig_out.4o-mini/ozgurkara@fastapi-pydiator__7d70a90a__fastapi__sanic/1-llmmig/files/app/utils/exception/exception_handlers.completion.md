### Explanation of Changes

To migrate the code from using the `fastapi` library to the `sanic` library, the following changes were made:

1. **Import Changes**: The `fastapi` and `starlette` imports were replaced with `sanic` equivalents. Specifically, `HTTPException` and `JSONResponse` were removed since `sanic` handles exceptions differently and uses a different response mechanism.
  
2. **Response Handling**: The `JSONResponse` from `fastapi` was replaced with `sanic.response.json`, which is the way to return JSON responses in `sanic`.

3. **Exception Handling**: The `HTTPException` from `fastapi` was removed, as `sanic` does not require it in the same way. Instead, we directly use the `response` object to handle errors.

4. **Status Codes**: The status codes are now directly imported from `sanic.response` instead of `starlette`.

Here is the modified code:

```python
import traceback
from typing import Optional, List

from sanic import Sanic
from sanic.response import json
from sanic.exceptions import SanicException

from app.utils.error.error_models import ErrorInfoModel
from app.utils.error.error_response import ErrorResponseModel, ErrorInfoContainer
from app.utils.exception.exception_types import DataException, ServiceException


class ExceptionHandlers:

    @staticmethod
    def unhandled_exception(request, exc: Exception):
        return json(
            ExceptionHandlers.__get_error_content(
                error_info=ErrorInfoContainer.unhandled_error,
                error_detail=[ExceptionHandlers.__get_stack_trace(exc)]
            ),
            status=500
        )

    @staticmethod
    def data_exception(request, exc: DataException):
        return json(
            ExceptionHandlers.__get_error_content(
                error_info=exc.error_info
            ),
            status=400
        )

    @staticmethod
    def service_exception(request, exc: ServiceException):
        return json(
            ExceptionHandlers.__get_error_content(
                error_info=exc.error_info
            ),
            status=400
        )

    @staticmethod
    def http_exception(request, exc: SanicException):
        return json(
            ExceptionHandlers.__get_error_content(
                error_info=ErrorInfoContainer.unhandled_error,
                error_detail=[exc.args[0]]
            ),
            status=exc.status_code
        )

    @staticmethod
    def validation_exception(request, exc):
        return json(
            ExceptionHandlers.__get_error_content(
                error_info=ErrorInfoContainer.model_validation_error,
                error_detail=exc.args[0]
            ),
            status=422
        )

    @staticmethod
    def __get_error_content(error_info: ErrorInfoModel, error_detail: Optional[List] = None):
        return {
            "error_code": error_info.code,
            "error_message": error_info.message,
            "error_detail": error_detail,
        }

    @staticmethod
    def __get_stack_trace(exc: Exception) -> str:
        return "".join(traceback.TracebackException.from_exception(exc).format())
```

This code now uses `sanic` for handling HTTP requests and responses, while maintaining the original structure and functionality of the exception handling logic.