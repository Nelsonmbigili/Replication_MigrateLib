### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Importing aiohttp**: The `aiohttp` library was imported instead of `requests`.
2. **Session Management**: The `Session` object from `requests` was replaced with `aiohttp.ClientSession`. This requires using an asynchronous context manager to ensure proper session management.
3. **Asynchronous Requests**: The `request` and `raw_request` methods were modified to be asynchronous (`async def`) and use `await` for making requests with `aiohttp`.
4. **Response Handling**: The response handling was adjusted to work with `aiohttp`'s response object, which requires using `await response.json()` for JSON responses.
5. **Timeout Handling**: The timeout handling was adapted to use `aiohttp.ClientTimeout`.
6. **Error Handling**: The error handling was updated to accommodate the asynchronous nature of `aiohttp`.

### Modified Code

Here is the complete modified code after migrating to `aiohttp`:

```python
import json
import logging
from typing import Any, NoReturn, Optional

from aiohttp import ClientSession, ClientTimeout, ClientResponse
from aiohttp.client_exceptions import ClientError

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

        self.session = ClientSession(timeout=ClientTimeout(total=self.host_timeout))
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

    async def request(
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
                async with self.session.request(
                    method=method, url=url, json=payload
                ) as response:
                    await self.__handle_response(response)
                    return GreenAPIResponse(response.status, await response.text())
            else:
                async with self.session.request(
                    method=method, url=url, data=payload, files=files
                ) as response:
                    await self.__handle_response(response)
                    return GreenAPIResponse(response.status, await response.text())
        except ClientError as error:
            error_message = f"Request was failed with error: {error}."

            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)

            return GreenAPIResponse(None, error_message)

    async def raw_request(self, **arguments: Any) -> GreenAPIResponse:
        try:
            async with self.session.request(**arguments) as response:
                await self.__handle_response(response)
                return GreenAPIResponse(response.status, await response.text())
        except ClientError as error:
            error_message = f"Request was failed with error: {error}."

            if self.raise_errors:
                raise GreenAPIError(error_message)
            self.logger.log(logging.CRITICAL, error_message)

            return GreenAPIResponse(None, error_message)

    async def __handle_response(self, response: ClientResponse) -> Optional[NoReturn]:
        status_code = response.status
        if status_code != 200 or self.debug_mode:
            try:
                data = json.dumps(
                    await response.json(), ensure_ascii=False, indent=4
                )
            except json.JSONDecodeError:
                data = await response.text()

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
        self.session.headers["Connection"] = "close"

        # aiohttp does not have a built-in retry mechanism like requests
        # You may need to implement your own retry logic if necessary


class GreenAPI(GreenApi):
    pass


class GreenAPIError(Exception):
    pass
```

### Note
- The `__prepare_session` method was left unchanged regarding retries, as `aiohttp` does not have a built-in retry mechanism like `requests`. You may need to implement custom retry logic if required.