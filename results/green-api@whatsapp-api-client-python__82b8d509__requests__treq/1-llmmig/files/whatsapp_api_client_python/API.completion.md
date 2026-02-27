### Explanation of Changes
To migrate the code from the `requests` library to the `treq` library, the following changes were made:
1. **Session Management**: The `requests.Session` object and its configuration (e.g., retries, headers) were removed because `treq` does not use session objects. Instead, `treq` relies on `twisted`'s asynchronous HTTP client.
2. **Request Handling**: The `session.request` calls were replaced with `treq`'s asynchronous request methods (`treq.request`).
3. **Timeouts**: `treq` uses a `reactor`-based timeout mechanism, so the `timeout` parameter was passed directly to the `treq` request calls.
4. **Response Handling**: `treq` returns a `Deferred` object, so the response handling was updated to use asynchronous methods like `response.text()` and `response.code`.
5. **Error Handling**: Exceptions were updated to handle `twisted`-specific errors where necessary.
6. **Initialization**: The `__prepare_session` method was removed since `treq` does not require session preparation.

### Modified Code
```python
import json
import logging
from typing import Any, NoReturn, Optional

import treq
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.error import TimeoutError

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

    @inlineCallbacks
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
                response = yield treq.request(
                    method=method,
                    url=url,
                    json=payload,
                    timeout=self.host_timeout
                )
            else:
                response = yield treq.request(
                    method=method,
                    url=url,
                    data=payload,
                    files=files,
                    timeout=self.media_timeout
                )
        except TimeoutError as error:
            error_message = f"Request timed out: {error}."
            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)
            returnValue(GreenAPIResponse(None, error_message))
        except Exception as error:
            error_message = f"Request failed with error: {error}."
            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)
            returnValue(GreenAPIResponse(None, error_message))

        yield self.__handle_response(response)

        text = yield response.text()
        returnValue(GreenAPIResponse(response.code, text))

    @inlineCallbacks
    def raw_request(self, **arguments: Any) -> GreenAPIResponse:
        try:
            response = yield treq.request(**arguments)
        except TimeoutError as error:
            error_message = f"Request timed out: {error}."
            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)
            returnValue(GreenAPIResponse(None, error_message))
        except Exception as error:
            error_message = f"Request failed with error: {error}."
            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)
            returnValue(GreenAPIResponse(None, error_message))

        yield self.__handle_response(response)

        text = yield response.text()
        returnValue(GreenAPIResponse(response.code, text))

    @inlineCallbacks
    def __handle_response(self, response) -> Optional[NoReturn]:
        status_code = response.code
        if status_code != 200 or self.debug_mode:
            try:
                text = yield response.text()
                data = json.dumps(json.loads(text), ensure_ascii=False, indent=4)
            except json.JSONDecodeError:
                data = yield response.text()

            if status_code != 200:
                error_message = (
                    f"Request failed with status code: {status_code}."
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


class GreenAPI(GreenApi):
    pass


class GreenAPIError(Exception):
    pass
```

### Key Notes
- The `@inlineCallbacks` decorator is used to handle asynchronous code in a synchronous-like manner.
- `returnValue` is used to return values from asynchronous functions.
- The `treq` library does not have a session concept, so session-related code was removed.
- The `timeout` parameter is passed directly to `treq.request` calls.