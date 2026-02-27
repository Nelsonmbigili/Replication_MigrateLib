### Explanation of Changes

To migrate the code from `requests` to `aiohttp`, the following changes were made:

1. **Import Changes**:
   - Removed the `requests` import and replaced it with `aiohttp`.

2. **Asynchronous Programming**:
   - Since `aiohttp` is asynchronous, the `_request` method was converted to an `async` function.
   - Any calls to `request` were replaced with `aiohttp.ClientSession` and its methods (e.g., `session.request`).

3. **Session Management**:
   - An `aiohttp.ClientSession` is used to manage HTTP requests. This session is created and used within the `_request` method.

4. **Data Handling**:
   - The `data` parameter in `aiohttp` is replaced with `json` for JSON payloads.
   - The `params` parameter remains the same for query parameters.

5. **Response Handling**:
   - The `aiohttp` response object is used to extract JSON or text content using `await res.json()` or `await res.text()`.

6. **Error Handling**:
   - `aiohttp` raises exceptions for HTTP errors (e.g., `aiohttp.ClientResponseError`), so explicit error handling was added to raise `ApiException` for non-2xx responses.

7. **Logging**:
   - Adjusted logging to accommodate the asynchronous nature of `aiohttp`.

### Modified Code

```python
import json
import logging
import os
from json import JSONDecodeError
from urllib.parse import urljoin
import aiohttp
from aiohttp import ClientResponseError

from rest_client.base.authentication import Authentication
from rest_client.base.util import fill_query_params
from rest_client.log_config import logger_config
from rest_client.base.config import BaseUrlConfig, RequestConfig, ApiResponse
from rest_client.base.variables import CONTENT_TYPE, ENV
from rest_client.__version__ import __version__
from rest_client.base.exceptions import ApiException

log = logger_config(__name__, logging.INFO)


class NoEndpointsExceptions(Exception):
    pass


class Client:
    user_agent = f'saleweaver-base-client-{__version__}'

    @property
    def endpoints(self) -> dict:
        return self._endpoints

    @endpoints.setter
    def endpoints(self, endpoints):
        self._endpoints = endpoints

    @property
    def base_url_config(self) -> BaseUrlConfig:
        return self._base_url_config

    @base_url_config.setter
    def base_url_config(self, base_url_config: BaseUrlConfig):
        self._base_url_config = base_url_config

    def __init__(self, authentication_handler: Authentication = None):
        self._endpoints = {}
        self._base_url_config = None
        self.auth = authentication_handler
        self.method: str = 'GET'
        self.content_type: str = os.environ.get(CONTENT_TYPE, 'application/json;charset=UTF-8')

    @property
    def headers(self):
        return {
            'Content-Type': self.content_type,
            'User-Agent': self.user_agent
        }

    def _path(self, path):
        path = path.lstrip('/')
        if os.environ.get(ENV, None) == 'SANDBOX':
            return urljoin(self.base_url_config.sandbox_url, path)
        return urljoin(self.base_url_config.base_url, path)

    async def _request(self, data: dict, *args, **kwargs) -> ApiResponse:
        request_config: RequestConfig = data.pop('request_config')
        log.debug(request_config)
        self._log_request(args, data, kwargs, request_config)

        async with aiohttp.ClientSession(auth=self.auth) as session:
            try:
                async with session.request(
                    request_config.method,
                    self._path(request_config.path),
                    headers=kwargs.pop('headers', self.headers),
                    json=data.get('payload') if data and request_config.method in ('POST', 'PUT', 'PATCH') else None,
                    params=data if request_config.method in ('GET', 'DELETE') else None,
                ) as res:
                    self._log_response(res)

                    try:
                        response = await res.json()
                    except JSONDecodeError:
                        response = await res.text()

                    if 200 <= res.status < 400:
                        return ApiResponse(response, res.headers, res.status)
                    raise ApiException(response, res.headers, res.status)
            except ClientResponseError as e:
                log.error(f"HTTP error occurred: {e}")
                raise ApiException(str(e), {}, e.status)

    def _log_request(self, args, data, kwargs, request_config):
        log.debug('Requesting %s', (self._path(request_config.path)))
        log.debug(kwargs.get('headers', self.headers))
        log.debug(request_config)
        log.debug(data)
        log.debug(args)
        log.debug(kwargs)

    def _log_response(self, res):
        log.debug(res.request_info.headers)
        log.debug(res.status)
        log.debug(res.headers)

    def __getattr__(self, item):
        log.debug(f'Requesting endpoint: {item}')
        log.debug(self.endpoints)

        if self.endpoints.get(item, None):
            def wrapper(*args, **kwargs):
                log.debug('called with %r and %r' % (args, kwargs))
                return self.method_template(self.endpoints.get(item))(*args, **kwargs)

            return wrapper
        raise AttributeError(f'{item} does not exist, possible calls: {self.endpoints.keys()}')

    def method_template(self, _endpoint):
        def fn(*args, **kwargs):
            _endpoint.path = fill_query_params(_endpoint.path, *args)
            kwargs.update({
                'request_config': _endpoint
            })
            return self._request(kwargs)

        return fn
```

### Key Notes:
- The `_request` method is now asynchronous, so any calls to it must use `await`.
- The `aiohttp.ClientSession` is used for making HTTP requests, and it is properly closed after use with an `async with` block.
- Error handling for HTTP responses has been updated to handle `aiohttp` exceptions.
- The rest of the code remains unchanged to ensure compatibility with the larger application.