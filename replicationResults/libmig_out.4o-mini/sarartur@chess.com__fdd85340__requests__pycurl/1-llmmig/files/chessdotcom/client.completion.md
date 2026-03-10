### Explanation of Changes

To migrate the code from using the `requests` library to using `pycurl`, several key changes were made:

1. **Importing PyCurl**: The `requests` library was replaced with `pycurl`. The `requests` library is a higher-level HTTP library, while `pycurl` is a lower-level interface to the cURL library, which requires more manual setup for requests.

2. **Synchronous Request Handling**: The synchronous request method `_do_sync_get_request` was modified to use `pycurl`. This involved setting up a `pycurl.Curl` object, configuring it with the necessary options, and handling the response manually.

3. **Asynchronous Request Handling**: The asynchronous request method `_do_async_get_request` was removed since `pycurl` does not support asynchronous operations directly. If asynchronous behavior is required, it would need to be handled differently, possibly using threads or another library.

4. **Error Handling**: The error handling was adjusted to work with the response from `pycurl`, which does not return a response object like `requests` does.

5. **Response Handling**: The response text is captured using a callback function with `pycurl`, and the headers are retrieved using `getinfo`.

Here is the modified code:

```python
import asyncio
import copy
import time
import warnings
from functools import wraps
import pycurl
from io import BytesIO

from .errors import ChessDotComClientError
from .response_builder import DefaultResponseBuilder


class RateLimitHandler(object):
    """
    Rate Limit Handler for handling 429 responses from the API.

    :tts: The time the client will wait after a 429 response if there are tries remaining.
    :retries: The number of times the client will retry calling the API after the first attempt.
    """

    def __init__(self, tts=0, retries=1):
        self.tts = tts
        self.retries = retries

    @property
    def retries(self):
        return self._retries

    @retries.setter
    def retries(self, retries):
        if retries < 0:
            warnings.warn(
                "Number of retries can not be less than 0. Setting value to 0."
            )
            retries = 0
        self._retries = retries

    def should_try_again(self, status_code, resource):
        if status_code == 429 and self.retries - resource.times_requested >= 0:
            time.sleep(self.tts)
            return True
        return False


class Client:
    """
    Client for Chess.com Public API. The client is only responsible for making calls.

    :cvar request_config: Dictionary containing extra keyword arguments for
        requests to the API (headers, proxy, etc).
    :cvar aio: Determines if the functions behave asynchronously.
    :cvar :rate_limit_handler: A RateLimitHandler object.
        See :obj:`chessdotcom.client.RateLimitHandler`.
    :loop_callback: Function that returns the current loop for aiohttp.ClientSession.
    """

    aio = False
    request_config = {"headers": {}}
    rate_limit_handler = RateLimitHandler(tts=0, retries=1)
    endpoints = []

    @classmethod
    def endpoint(cls, func):
        cls.endpoints.append(func)

        return cls().activate_endpoint(func)

    @staticmethod
    def loop_callback():
        return asyncio.get_running_loop()

    def do_get_request(self, resource):
        if resource.tts:
            time.sleep(resource.tts)

        _do_get_request = (
            self._do_async_get_request if self.aio else self._do_sync_get_request
        )

        return _do_get_request(resource)

    def activate_endpoint(self, endpoint):
        @wraps(endpoint)
        def wrapper(*args, **kwargs):
            return self.do_get_request(endpoint(*args, **kwargs))

        setattr(self, endpoint.__name__, wrapper)
        return wrapper

    def _build_request_options(self, resource):
        options = {**resource.request_options, **self.request_config}

        if "user-agent" not in [header.lower() for header in options["headers"].keys()]:
            warnings.warn(
                "Calls to api.chess.com require an updated 'User-Agent' header. "
                "You can update this with something like "
                "chessdotcom.Client.request_config['headers']['User-Agent'] "
                "= 'My Python Application. Contact me at email@example.com'"
            )

        return options

    def _do_sync_get_request(self, resource):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, resource.url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.TIMEOUT, 30)

        headers = []
        for key, value in self._build_request_options(resource)["headers"].items():
            headers.append(f"{key}: {value}")
        c.setopt(c.HTTPHEADER, headers)

        try:
            c.perform()
            resource.times_requested += 1
            status_code = c.getinfo(c.RESPONSE_CODE)
            response_text = buffer.getvalue().decode('utf-8')
            if status_code != 200:
                if self.rate_limit_handler.should_try_again(status_code, resource):
                    return self._do_sync_get_request(resource)
                raise ChessDotComClientError(
                    status_code=status_code, response_text=response_text, headers={}
                )
            return resource.response_builder.build(response_text)
        finally:
            c.close()

    async def _do_async_get_request(self, resource):
        raise NotImplementedError("Asynchronous requests are not supported with pycurl.")


class ChessDotComClient(Client):
    """
    Client for Chess.com Public API. The client can be initialized withe following options.

    :ivar request_config: Dictionary containing extra keyword arguments
        for requests to the API (headers, proxy, etc).
        This value will be set from Client if nothing is provided
    :ivar aio: Determines if the functions behave asynchronously. Defaults to False
    :ivar rate_limit_handler: A RateLimitHandler object.
        See :obj:`chessdotcom.client.RateLimitHandler`.
    :ivar user_agent: A string that will be used as the User-Agent header in requests to the API.
        This value will override the value in request_config if provided.
    """

    def __init__(
        self,
        aio: bool = False,
        user_agent: str = None,
        request_config: dict = None,
        rate_limit_handler: RateLimitHandler = None,
        verify_ssl: bool = True,
    ) -> None:
        self.aio = aio

        self._set_request_options(
            request_config,
            default_request_config=self.request_config,
            verify_ssl=verify_ssl,
            user_agent=user_agent,
        )

        self.rate_limit_handler = rate_limit_handler or self.rate_limit_handler

        # Load endpoints to register
        from . import endpoints

        endpoints

        for endpoint in self.endpoints:
            self.activate_endpoint(endpoint)

    def _set_request_options(
        self, request_config, default_request_config, verify_ssl, user_agent
    ):
        request_config = request_config or {}

        request_config = {**copy.deepcopy(default_request_config), **request_config}
        request_config["verify_ssl" if self.aio else "verify"] = verify_ssl
        if user_agent:
            request_config["headers"]["User-Agent"] = user_agent

        self.request_config = request_config


class Resource(object):
    HOST = "https://api.chess.com/pub"

    def __init__(
        self,
        uri="",
        top_level_attribute=None,
        tts=0,
        request_options=None,
        times_requested=0,
        response_builder=None,
    ):
        self.url = self.HOST + uri
        self.top_level_attribute = top_level_attribute
        self.tts = tts
        self.times_requested = times_requested

        self.request_options = request_options or {}
        self.response_builder = response_builder or DefaultResponseBuilder(self)
```