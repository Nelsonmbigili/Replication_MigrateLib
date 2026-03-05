import json
import logging
from typing import Any, NoReturn, Optional
import pycurl
from io import BytesIO

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
            host_timeout: float = 180, # sec per retry
            media_timeout: float = 10800, # sec per retry
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

        buffer = BytesIO()
        response_code = None
        try:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.WRITEFUNCTION, buffer.write)
            c.setopt(c.TIMEOUT, self.host_timeout)

            if method.upper() == 'POST':
                c.setopt(c.POST, 1)
                if files:
                    # Handle file uploads if necessary
                    # This part may need additional handling based on how files are structured
                    pass
                else:
                    c.setopt(c.POSTFIELDS, json.dumps(payload))
                    c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])

            response_code = c.perform()
            c.close()
        except pycurl.error as error:
            error_message = f"Request was failed with error: {error}."

            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)

            return GreenAPIResponse(None, error_message)

        response_body = buffer.getvalue().decode('utf-8')
        self.__handle_response(response_code, response_body)

        return GreenAPIResponse(response_code, response_body)

    def raw_request(self, **arguments: Any) -> GreenAPIResponse:
        # This method can be implemented similarly to request() using pycurl
        pass

    def __handle_response(self, response_code: int, response_body: str) -> Optional[NoReturn]:
        if response_code != 200 or self.debug_mode:
            try:
                data = json.dumps(
                    json.loads(response_body), ensure_ascii=False, indent=4
                )
            except json.JSONDecodeError:
                data = response_body

            if response_code != 200:
                error_message = (
                    f"Request was failed with status code: {response_code}."
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
        # Session preparation is not needed for pycurl
        pass


class GreenAPI(GreenApi):
    pass


class GreenAPIError(Exception):
    pass
