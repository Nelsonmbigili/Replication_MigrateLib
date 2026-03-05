import logging
from typing import Dict

from sanic import Sanic
from sanic.response import json
from sanic.exceptions import SanicException

from .api_evaluate import get_evaluate_router
from .api_sample_size_calculation import get_sample_size_calculation_router
from .api_settings import ApiSettings
from .json_response import DataScienceJsonResponse


def get_api(settings: ApiSettings, get_dao, get_executor_pool) -> Sanic:
    api = Sanic(
        name=settings.app_title,
        version="0.2.1",
    )

    @api.exception(SanicException)
    async def custom_http_exception_handler(request, exc):
        """
        We override default exception handler to send exception to the log.
        """
        logger = logging.getLogger("epstats")
        logger.error(f"HttpException status code [{exc.status}] detail [{exc.args}]")
        return json({"error": str(exc)}, status=exc.status)

    @api.exception(RequestValidationError)
    async def custom_request_validation_exception_handler(request, exc):
        """
        We override default exception handler to send exception to the log.
        """
        logger = logging.getLogger("epstats")
        logger.exception(f"RequestValidationError: [{exc}], [{exc.body}]")
        return json({"error": "Request validation error"}, status=400)

    @api.get("/health", tags=["Health"])
    async def readiness_liveness_probe(request):
        return json({"message": "ep-stats-api is ready"})

    api.blueprint(get_evaluate_router(get_dao, get_executor_pool))
    api.blueprint(get_sample_size_calculation_router(get_executor_pool))

    return api


def serve(api: Sanic, settings: ApiSettings, log_config: Dict):
    logger = logging.getLogger("epstats")
    logger.info(f"Starting {settings.app_name} in env {settings.app_env}")
    logger.info(f"Listening on http://{settings.host}:{settings.port}")
    logger.info(f"Starting with log level {settings.log_level}")
    logger.info(f"Using {settings.web_workers} web server worker threads")
    api.run(
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        workers=settings.web_workers,
        timeout=0,
    )
