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
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from app.resources.health_check import health_check_resource
from app.resources.todo import todo_resource
from fastapi import FastAPI

from fastapi_contrib.common.middlewares import StateRequestIDMiddleware
from app.utils.exception.exception_handlers import ExceptionHandlers
from app.utils.pydiator.pydiator_core_config import set_up_pydiator
from app.utils.exception.exception_types import DataException, ServiceException


def create_app():
    app = FastAPI(
        title="FastAPI Pydiator",
        description="FastAPI pydiator integration project",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/",
        redoc_url="/redoc"
    )

    app.add_exception_handler(Exception, ExceptionHandlers.unhandled_exception)
    app.add_exception_handler(DataException, ExceptionHandlers.data_exception)
    app.add_exception_handler(ServiceException, ExceptionHandlers.service_exception)
    app.add_exception_handler(HTTPException, ExceptionHandlers.http_exception)
    app.add_exception_handler(ValidationError, ExceptionHandlers.validation_exception)

    app.include_router(
        health_check_resource.router,
        prefix="/health-check",
        tags=["health check"]
    )

    app.include_router(
        todo_resource.router,
        prefix="/v1/todos",
        tags=["todo"]
    )

    set_up_pydiator()

    return app

```