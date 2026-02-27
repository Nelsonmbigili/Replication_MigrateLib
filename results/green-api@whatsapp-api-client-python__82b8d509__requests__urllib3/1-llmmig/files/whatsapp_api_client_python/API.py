import json
import logging
from typing import Any, NoReturn, Optional

from urllib3 import PoolManager
from urllib3.util.retry import Retry
from urllib3.util.timeout import Timeout
from urllib3.exceptions import HTTPError

from .response import Response as GreenAPIResponse
from .tools import (
    account,
    device,
    groups,
    journals,
    marking,
    queues,
    receiving,
    sending,
    serviceMethods,
    webhooks
)


class GreenApi:
    host: str
    media: str
    idInstance: str
    apiTokenInstance: str

    def __init__(
            self,
            idInstance: str,
            apiTokenInstance: str,
            debug_mode: bool = False,
            raise_errors: bool = False,
            host: str = "https://api.green-api.com",
            media: str = "https://media.green-api.com",
            host_timeout: float = 180,  # sec per retry
            media_timeout: float = 10800,  # sec per retry
    ):
        self.host = host
        self.media = media
        self.debug_mode = debug_mode
        self.raise_errors = raise_errors

        # Change default values in init() if required
        self.host_timeout = host_timeout
        self.media_timeout = media_timeout

        self.idInstance = idInstance
        self.apiTokenInstance = apiTokenInstance

        self.session = PoolManager(headers={"Connection": "close"})
        self.__prepare_session()

        self.account = account.Account(self)
        self.device = device.Device(self)
        self.groups = groups.Groups(self)
        self.journals = journals.Journals(self)
        self.marking = marking.Marking(self)
        self.queues = queues.Queues(self)
        self.receiving = receiving.Receiving(self)
        self.sending = sending.Sending(self)
        self.serviceMethods = serviceMethods.ServiceMethods(self)
        self.webhooks = webhooks.Webhooks(self)

        self.logger = logging.getLogger("whatsapp-api-client-python")
        self.__prepare_logger()

    def request(
            self,
            method: str,
            url: str,
            payload: Optional[dict] = None,
            files: Optional[dict] = None
    ) -> GreenAPIResponse:
        url = url.replace("{{host}}", self.host)
        url = url.replace("{{media}}", self.media)
        url = url.replace("{{idInstance}}", self.idInstance)
        url = url.replace("{{apiTokenInstance}}", self.apiTokenInstance)

        try:
            timeout = Timeout(connect=self.host_timeout, read=self.host_timeout)
            if not files:
                response = self.session.request(
                    method=method,
                    url=url,
                    body=json.dumps(payload).encode('utf-8') if payload else None,
                    headers={"Content-Type": "application/json"},
                    timeout=timeout
                )
            else:
                # Note: urllib3 does not natively support multipart file uploads like requests.
                raise NotImplementedError("File uploads are not supported with urllib3 in this implementation.")
        except HTTPError as error:
            error_message = f"Request was failed with error: {error}."

            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)

            return GreenAPIResponse(None, error_message)

        self.__handle_response(response)

        return GreenAPIResponse(response.status, response.data.decode('utf-8'))

    def raw_request(self, **arguments: Any) -> GreenAPIResponse:
        try:
            response = self.session.request(**arguments)
        except HTTPError as error:
            error_message = f"Request was failed with error: {error}."

            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)

            return GreenAPIResponse(None, error_message)

        self.__handle_response(response)

        return GreenAPIResponse(response.status, response.data.decode('utf-8'))

    def __handle_response(self, response) -> Optional[NoReturn]:
        status_code = response.status
        if status_code != 200 or self.debug_mode:
            try:
                data = json.dumps(
                    json.loads(response.data.decode('utf-8')), ensure_ascii=False, indent=4
                )
            except json.JSONDecodeError:
                data = response.data.decode('utf-8')

            if status_code != 200:
                error_message = (
                    f"Request was failed with status code: {status_code}."
                    f" Data: {data}"
                )

                if self.raise_errors:
                    raise GreenAPIError(error_message)
                self.logger.log(logging.ERROR, error_message)

                return None

            self.logger.log(
                logging.DEBUG, f"Request was successful with data: {data}"
            )

    def __prepare_logger(self) -> None:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            (
                "%(asctime)s:%(name)s:"
                "%(levelname)s:%(message)s"
            ), datefmt="%Y-%m-%d %H:%M:%S"
        ))

        self.logger.addHandler(handler)

        if not self.debug_mode:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(logging.DEBUG)

    def __prepare_session(self) -> None:
        retry = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429]
        )
        self.session.retries = retry


class GreenAPI(GreenApi):
    pass


class GreenAPIError(Exception):
    pass
