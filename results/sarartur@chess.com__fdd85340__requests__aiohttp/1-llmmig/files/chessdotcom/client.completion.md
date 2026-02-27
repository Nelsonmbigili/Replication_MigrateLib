### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Synchronous Requests (`requests`) to Asynchronous Requests (`aiohttp`)**:
   - The `_do_sync_get_request` method, which used `requests.get`, was removed since `aiohttp` is designed for asynchronous operations.
   - The `_do_async_get_request` method was updated to handle all HTTP requests using `aiohttp.ClientSession`.

2. **Timeout Handling**:
   - The `timeout` parameter in `requests.get` was replaced with `aiohttp.ClientTimeout` in the `aiohttp` session.

3. **Rate Limiting**:
   - The `time.sleep` function in the `RateLimitHandler` was replaced with `asyncio.sleep` to ensure compatibility with asynchronous code.

4. **Session Management**:
   - The `aiohttp.ClientSession` is used for all HTTP requests, and it is properly managed using an asynchronous context (`async with`).

5. **Error Handling**:
   - The `status_code` attribute from `requests` was replaced with `status` from `aiohttp`.

6. **Text Response**:
   - The `r.text` from `requests` was replaced with `await r.text()` in `aiohttp`.

### Modified Code
Below is the entire code after migrating to `aiohttp`:

```python
import asyncio
import copy
import warnings
from functools import wraps

from aiohttp import ClientSession, ClientTimeout

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

    async def should_try_again(self, status_code, resource):
        if status_code == 429 and self.retries - resource.times_requested >= 0:
            await asyncio.sleep(self.tts)
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
            self._do_async_get_request if self.aio else self._do_async_get_request
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

    async def _do_async_get_request(self, resource):
        timeout = ClientTimeout(total=30)
        async with ClientSession(loop=self.loop_callback(), timeout=timeout) as session:
            async with session.get(
                url=resource.url, **self._build_request_options(resource)
            ) as r:
                text = await r.text()
                resource.times_requested += 1

                if r.status != 200:
                    if await self.rate_limit_handler.should_try_again(r.status, resource):
                        return await self._do_async_get_request(resource)
                    raise ChessDotComClientError(
                        status_code=r.status, response_text=text, headers=r.headers
                    )
                return resource.response_builder.build(text)


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
        request_config["ssl"] = verify_ssl
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

### Summary
The migration involved replacing synchronous `requests` calls with asynchronous `aiohttp` calls, ensuring proper session management, and adapting rate-limiting and error-handling logic to work in an asynchronous context.