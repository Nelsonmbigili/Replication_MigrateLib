### Explanation of Changes

To migrate the code from `requests` to `aiohttp`, the following changes were made:

1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so the `_rest_request` method and any methods calling it need to be converted to `async` functions.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` for making requests. A session is created and used for all HTTP requests.
3. **Request Methods**: The `requests` methods (`get`, `post`, `put`, `delete`) were replaced with their `aiohttp` equivalents (`session.get`, `session.post`, etc.).
4. **Timeout Handling**: `aiohttp` uses `aiohttp.ClientTimeout` for timeout configuration.
5. **Error Handling**: `aiohttp` raises `aiohttp.ClientError` for connection-related errors, so the exception handling was updated accordingly.
6. **Response Handling**: `aiohttp` responses need to be explicitly read using `await response.text()`.

Below is the modified code:

---

### Modified Code
```python
"""
SamsungTVWS - Samsung Smart TV WS API wrapper

Copyright (C) 2019 DSR! <xchwarze@gmail.com>

SPDX-License-Identifier: LGPL-3.0
"""

import logging
from typing import Any, Dict, Optional

import aiohttp

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
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout)
        )

    async def _rest_request(self, target: str, method: str = "GET") -> Dict[str, Any]:
        url = self._format_rest_url(target)
        try:
            if method == "POST":
                async with self._session.post(url, ssl=False) as response:
                    response_text = await response.text()
            elif method == "PUT":
                async with self._session.put(url, ssl=False) as response:
                    response_text = await response.text()
            elif method == "DELETE":
                async with self._session.delete(url, ssl=False) as response:
                    response_text = await response.text()
            else:
                async with self._session.get(url, ssl=False) as response:
                    response_text = await response.text()
            return helper.process_api_response(response_text)
        except aiohttp.ClientError as err:
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

    async def close(self) -> None:
        """Close the aiohttp session."""
        await self._session.close()
```

---

### Key Notes:
1. **Session Management**: The `aiohttp.ClientSession` is created in the constructor and reused for all requests. A `close` method is added to properly close the session when the object is no longer needed.
2. **Asynchronous Methods**: All methods that interact with `_rest_request` are now `async` and must be awaited when called.
3. **SSL Verification**: The `ssl=False` parameter is used to disable SSL verification, similar to `verify=False` in `requests`.

This code is now fully migrated to use `aiohttp` and is ready for asynchronous execution.