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
