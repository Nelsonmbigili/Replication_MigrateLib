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
