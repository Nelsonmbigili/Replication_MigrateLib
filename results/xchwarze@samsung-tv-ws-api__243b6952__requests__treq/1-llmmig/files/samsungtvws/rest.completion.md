### Explanation of Changes:
To migrate the code from the `requests` library to the `treq` library, the following changes were made:
1. **Asynchronous Nature of `treq`**: `treq` is an asynchronous library, so the `_rest_request` method was converted to an `async` function. All calls to `requests` methods (e.g., `requests.get`, `requests.post`) were replaced with their `treq` equivalents (e.g., `treq.get`, `treq.post`).
2. **Handling Responses**: `treq` methods return a `Response` object, which requires asynchronous methods (e.g., `response.text()` instead of `response.text`) to retrieve the response body.
3. **Error Handling**: `treq` does not raise exceptions like `requests.ConnectionError`. Instead, connection errors are handled by the underlying Twisted framework. To handle such errors, the `treq` request calls are wrapped in a `try-except` block, and `twisted.internet.error` exceptions are caught.
4. **Helper Function**: The `helper.process_api_response` function is assumed to work with the response text, so the response body is awaited and passed to this function.
5. **Calling Asynchronous Methods**: Since `_rest_request` is now asynchronous, all methods that call it (`rest_device_info`, `rest_app_status`, etc.) were also converted to `async` functions.

### Modified Code:
```python
"""
SamsungTVWS - Samsung Smart TV WS API wrapper

Copyright (C) 2019 DSR! <xchwarze@gmail.com>

SPDX-License-Identifier: LGPL-3.0
"""

import logging
from typing import Any, Dict, Optional

import treq
from twisted.internet.error import ConnectError

from . import connection, exceptions, helper

_LOGGING = logging.getLogger(__name__)


class SamsungTVRest(connection.SamsungTVWSBaseConnection):
    def __init__(
        self,
        host: str,
        port: int = 8001,
        timeout: Optional[float] = None,
    ) -> None:
        super().__init__(
            host,
            endpoint="",
            port=port,
            timeout=timeout,
        )

    async def _rest_request(self, target: str, method: str = "GET") -> Dict[str, Any]:
        url = self._format_rest_url(target)
        try:
            if method == "POST":
                response = await treq.post(url, timeout=self.timeout, verify=False)
            elif method == "PUT":
                response = await treq.put(url, timeout=self.timeout, verify=False)
            elif method == "DELETE":
                response = await treq.delete(url, timeout=self.timeout, verify=False)
            else:
                response = await treq.get(url, timeout=self.timeout, verify=False)
            
            response_text = await response.text()
            return helper.process_api_response(response_text)
        except ConnectError as err:
            raise exceptions.HttpApiError(
                "TV unreachable or feature not supported on this model."
            ) from err

    async def rest_device_info(self) -> Dict[str, Any]:
        _LOGGING.debug("Get device info via rest api")
        return await self._rest_request("")

    async def rest_app_status(self, app_id: str) -> Dict[str, Any]:
        _LOGGING.debug("Get app %s status via rest api", app_id)
        return await self._rest_request("applications/" + app_id)

    async def rest_app_run(self, app_id: str) -> Dict[str, Any]:
        _LOGGING.debug("Run app %s via rest api", app_id)
        return await self._rest_request("applications/" + app_id, "POST")

    async def rest_app_close(self, app_id: str) -> Dict[str, Any]:
        _LOGGING.debug("Close app %s via rest api", app_id)
        return await self._rest_request("applications/" + app_id, "DELETE")

    async def rest_app_install(self, app_id: str) -> Dict[str, Any]:
        _LOGGING.debug("Install app %s via rest api", app_id)
        return await self._rest_request("applications/" + app_id, "PUT")
```

### Key Points:
- The `_rest_request` method and all methods that call it are now `async`.
- `treq` methods are used for HTTP requests, and their responses are awaited to retrieve the response body.
- Connection errors are handled using `twisted.internet.error.ConnectError`.
- The rest of the code remains unchanged to ensure compatibility with the larger application.