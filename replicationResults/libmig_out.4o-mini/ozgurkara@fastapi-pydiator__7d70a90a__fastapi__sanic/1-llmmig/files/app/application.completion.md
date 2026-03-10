### Explanation of Changes

To migrate the code from using the `fastapi` library to the `sanic` library, several key changes were made:

1. **Import Statements**: The import statements were updated to use `sanic` and its components instead of `fastapi`. This includes changing the main application class from `FastAPI` to `Sanic`.

2. **Application Initialization**: The initialization of the application was modified to use `Sanic`'s constructor.

3. **Exception Handling**: The way exceptions are handled in `sanic` differs from `fastapi`. The `add_exception_handler` method is replaced with `@app.exception` decorators for handling exceptions.

4. **Routing**: The method for including routers was changed to use `add_route` or `add_blueprint` in `sanic`, depending on how the routers are structured. In this case, we assume the routers are structured as `Blueprints`.

5. **Middleware**: The middleware setup is different in `sanic`, so any middleware that was used in `fastapi` needs to be adapted to `sanic`'s middleware system.

Here is the modified code:

```python
from sanic import Sanic
from sanic.exceptions import SanicException
from pydantic import ValidationError

from app.resources.health_check import health_check_resource
from app.resources.todo import todo_resource
from app.utils.exception.exception_handlers import ExceptionHandlers
from app.utils.pydiator.pydiator_core_config import set_up_pydiator
from app.utils.exception.exception_types import DataException, ServiceException


def create_app():
    app = Sanic(
        "FastAPI Pydiator",
        description="FastAPI pydiator integration project",
        version="1.0.0"
    )

    @app.exception(Exception)
    async def handle_unhandled_exception(request, exception):
        return await ExceptionHandlers.unhandled_exception(request, exception)

    @app.exception(DataException)
    async def handle_data_exception(request, exception):
        return await ExceptionHandlers.data_exception(request, exception)

    @app.exception(ServiceException)
    async def handle_service_exception(request, exception):
        return await ExceptionHandlers.service_exception(request, exception)

    @app.exception(SanicException)
    async def handle_http_exception(request, exception):
        return await ExceptionHandlers.http_exception(request, exception)

    @app.exception(ValidationError)
    async def handle_validation_exception(request, exception):
        return await ExceptionHandlers.validation_exception(request, exception)

    app.blueprint(health_check_resource.router, url_prefix="/health-check")
    app.blueprint(todo_resource.router, url_prefix="/v1/todos")

    set_up_pydiator()

    return app
```

### Notes:
- The `Sanic` application is initialized with a title and description, but the `openapi_url`, `docs_url`, and `redoc_url` parameters are not directly applicable in `sanic` as they are in `fastapi`.
- The exception handling functions are defined as asynchronous functions to match `sanic`'s asynchronous nature.
- The routers are assumed to be `Blueprints` in `sanic`, which is a common practice for organizing routes. If they are not, further adjustments may be needed based on their actual implementation.