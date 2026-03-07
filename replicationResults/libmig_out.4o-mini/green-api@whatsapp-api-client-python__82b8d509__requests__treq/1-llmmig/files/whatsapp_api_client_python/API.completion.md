### Explanation of Changes

To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `treq`.
2. **Session Management**: The `Session` object from `requests` was removed since `treq` does not require a session object for making requests. Instead, `treq` handles connections automatically.
3. **Request Method**: The `self.session.request` calls were replaced with `treq.request`, which directly takes the method, URL, and other parameters.
4. **Timeout Handling**: The timeout parameter was directly passed to `treq.request` instead of being set in a session.
5. **Response Handling**: The response handling was adjusted to use `treq`'s response methods, specifically using `response.status_code` and `response.text` directly from the `treq` response object.

Here is the modified code:

```python
import json
import logging
from typing import Any, NoReturn, Optional

import treq

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

        self.__prepare_logger()

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
            if not files:
                response = treq.request(
                    method=method, url=url, json=payload, timeout=self.host_timeout
                )
            else:
                response = treq.request(
                    method=method, url=url, data=payload, files=files, timeout=self.media_timeout
                )
        except Exception as error:
            error_message = f"Request was failed with error: {error}."

            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)

            return GreenAPIResponse(None, error_message)

        self.__handle_response(response)

        return GreenAPIResponse(response.status_code, response.text)

    def raw_request(self, **arguments: Any) -> GreenAPIResponse:
        try:
            response = treq.request(**arguments)
        except Exception as error:
            error_message = f"Request was failed with error: {error}."

            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)

            return GreenAPIResponse(None, error_message)

        self.__handle_response(response)

        return GreenAPIResponse(response.status_code, response.text)

    def __handle_response(self, response) -> Optional[NoReturn]:
        status_code = response.status_code
        if status_code != 200 or self.debug_mode:
            try:
                data = json.dumps(
                    json.loads(response.text), ensure_ascii=False, indent=4
                )
            except json.JSONDecodeError:
                data = response.text

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
        pass  # Removed as treq does not require session preparation


class GreenAPI(GreenApi):
    pass


class GreenAPIError(Exception):
    pass
```