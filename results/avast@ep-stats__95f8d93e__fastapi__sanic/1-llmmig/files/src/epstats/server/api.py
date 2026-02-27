import logging
from typing import Dict

from sanic import Sanic
from sanic.exceptions import SanicException
from sanic.response import json

from .api_evaluate import get_evaluate_router
from .api_sample_size_calculation import get_sample_size_calculation_router
from .api_settings import ApiSettings


def get_api(settings: ApiSettings, get_dao, get_executor_pool) -> Sanic:
    app = Sanic(settings.app_title)

    @app.exception(SanicException)
    async def custom_http_exception_handler(request, exc):
        """
        We override default exception handler to send exception to the log.
        """
        logger = logging.getLogger("epstats")
        logger.error(f"HttpException status code [{exc.status_code}] detail [{exc.args[0]}]")
        return json({"error": exc.args[0]}, status=exc.status_code)

    @app.exception(Exception)
    async def custom_request_validation_exception_handler(request, exc):
        """
        We override default exception handler to send exception to the log.
        """
        logger = logging.getLogger("epstats")
        logger.exception(f"RequestValidationError: [{exc}]")
        return json({"error": "Request validation error"}, status=400)

    @app.get("/health")
    async def readiness_liveness_probe(request):
        return json({"message": "ep-stats-api is ready"})

    # Register blueprints (assuming the routers return Sanic blueprints)
    app.blueprint(get_evaluate_router(get_dao, get_executor_pool))
    app.blueprint(get_sample_size_calculation_router(get_executor_pool))

    return app


def serve(api: Sanic, settings: ApiSettings, log_config: Dict):
    logger = logging.getLogger("epstats")
    logger.info(f"Starting {settings.app_name} in env {settings.app_env}")
    logger.info(f"Listening on http://{settings.host}:{settings.port}")
    logger.info(f"Starting with log level {settings.log_level}")
    logger.info(f"Using {settings.web_workers} web server worker threads")
    api.run(
        host=settings.host,
        port=settings.port,
        workers=settings.web_workers,
        access_log=True,
        debug=settings.log_level.lower() == "debug",
    )
