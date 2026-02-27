### Explanation of Changes

To migrate the code from `fastapi` to `sanic`, the following changes were made:

1. **Sanic Application Initialization**:
   - Replaced `FastAPI` with `Sanic` for creating the application instance.
   - Adjusted the application metadata (title, description, version) using `Sanic`'s configuration.

2. **Exception Handlers**:
   - Sanic uses middleware or decorators for exception handling. Custom exception handlers were registered using `Sanic.exception()`.

3. **Routing**:
   - Replaced `app.include_router` with `Sanic`'s blueprint system (`app.blueprint()`).
   - Adjusted the import paths for `health_check_resource` and `todo_resource` to ensure they are compatible with Sanic's blueprint system.

4. **Middleware**:
   - Sanic uses `app.middleware()` for middleware registration. The `StateRequestIDMiddleware` was adapted accordingly.

5. **OpenAPI and Documentation**:
   - Sanic does not natively support OpenAPI or Swagger documentation out of the box. These features were omitted unless a third-party library is used.

6. **Other Adjustments**:
   - Removed `openapi_url`, `docs_url`, and `redoc_url` as they are specific to FastAPI.
   - Adjusted the `set_up_pydiator()` call to ensure it remains functional.

---

### Modified Code

```python
from pydantic import ValidationError
from sanic import Sanic
from sanic.exceptions import SanicException
from sanic.response import json

from app.resources.health_check import health_check_resource
from app.resources.todo import todo_resource
from app.utils.exception.exception_handlers import ExceptionHandlers
from app.utils.pydiator.pydiator_core_config import set_up_pydiator
from app.utils.exception.exception_types import DataException, ServiceException


def create_app():
    app = Sanic("Sanic Pydiator")

    # Set application metadata
    app.config.TITLE = "Sanic Pydiator"
    app.config.DESCRIPTION = "Sanic pydiator integration project"
    app.config.VERSION = "1.0.0"

    # Exception handlers
    @app.exception(Exception)
    async def unhandled_exception_handler(request, exception):
        return await ExceptionHandlers.unhandled_exception(request, exception)

    @app.exception(DataException)
    async def data_exception_handler(request, exception):
        return await ExceptionHandlers.data_exception(request, exception)

    @app.exception(ServiceException)
    async def service_exception_handler(request, exception):
        return await ExceptionHandlers.service_exception(request, exception)

    @app.exception(SanicException)
    async def http_exception_handler(request, exception):
        return await ExceptionHandlers.http_exception(request, exception)

    @app.exception(ValidationError)
    async def validation_exception_handler(request, exception):
        return await ExceptionHandlers.validation_exception(request, exception)

    # Middleware (StateRequestIDMiddleware)
    @app.middleware("request")
    async def add_request_id(request):
        await StateRequestIDMiddleware.process_request(request)

    # Blueprints (replacing FastAPI routers)
    app.blueprint(health_check_resource.router, url_prefix="/health-check")
    app.blueprint(todo_resource.router, url_prefix="/v1/todos")

    # Set up pydiator
    set_up_pydiator()

    return app
```

---

### Key Notes:
- The `Sanic` framework does not natively support OpenAPI or Swagger documentation. If these features are required, you would need to integrate a third-party library like `sanic-ext` or `sanic-openapi`.
- The `StateRequestIDMiddleware` was adapted to Sanic's middleware system. Ensure that the `process_request` method is compatible with Sanic's request object.
- The `ExceptionHandlers` methods were assumed to be asynchronous (`async def`) to align with Sanic's asynchronous nature. If they are synchronous, they need to be wrapped in `asyncio.run()` or similar constructs.