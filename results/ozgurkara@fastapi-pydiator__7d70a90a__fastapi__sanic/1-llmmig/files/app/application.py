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
