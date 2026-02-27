import traceback
from typing import Optional, List
from http import HTTPStatus

from sanic.exceptions import SanicException
from sanic.response import json

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
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

    @staticmethod
    def data_exception(request, exc: DataException):
        return json(
            ExceptionHandlers.__get_error_content(
                error_info=exc.error_info
            ),
            status=HTTPStatus.BAD_REQUEST,
        )

    @staticmethod
    def service_exception(request, exc: ServiceException):
        return json(
            ExceptionHandlers.__get_error_content(
                error_info=exc.error_info
            ),
            status=HTTPStatus.BAD_REQUEST,
        )

    @staticmethod
    def http_exception(request, exc: SanicException):
        return json(
            ExceptionHandlers.__get_error_content(
                error_info=ErrorInfoContainer.unhandled_error,
                error_detail=[exc.args[0]]  # SanicException stores the message in args[0]
            ),
            status=exc.status_code,
        )

    @staticmethod
    def validation_exception(request, exc):
        return json(
            ExceptionHandlers.__get_error_content(
                error_info=ErrorInfoContainer.model_validation_error,
                error_detail=exc.errors()  # Assuming exc.errors() is still valid
            ),
            status=HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    @staticmethod
    def __get_error_content(error_info: ErrorInfoModel, error_detail: Optional[List] = None):
        return ErrorResponseModel(
            error_code=error_info.code,
            error_message=error_info.message,
            error_detail=error_detail,
        ).dict()

    @staticmethod
    def __get_stack_trace(exc: Exception) -> str:
        return "".join(traceback.TracebackException.from_exception(exc).format())
