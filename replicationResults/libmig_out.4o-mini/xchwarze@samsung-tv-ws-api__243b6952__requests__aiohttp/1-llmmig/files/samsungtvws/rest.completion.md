### Explanation of Changes

To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Asynchronous Functionality**: The `aiohttp` library is designed for asynchronous programming, so the methods that perform HTTP requests need to be defined as asynchronous (`async def`), and the calls to these methods must be awaited.

2. **Session Management**: In `aiohttp`, it is common to create a session object to manage connections. This is done using `aiohttp.ClientSession()`, which is used to make requests.

3. **Request Methods**: The request methods (`get`, `post`, `put`, `delete`) are called on the session object instead of directly as in `requests`.

4. **Response Handling**: The response from `aiohttp` is an object that needs to be awaited to get the actual response data.

5. **Error Handling**: The error handling for connection issues is adapted to work with `aiohttp`.

Here is the modified code:

```python
"""
SamsungTVWS - Samsung Smart TV WS API wrapper

Copyright (C) 2019 DSR! <xchwarze@gmail.com>

SPDX-License-Identifier: LGPL-3.0
"""

import logging
from typing import Any, Dict, Optional
import aiohttp
import asyncio

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
        async with aiohttp.ClientSession() as session:
            try:
                if method == "POST":
                    async with session.post(url, timeout=self.timeout) as response:
                        response_text = await response.text()
                elif method == "PUT":
                    async with session.put(url, timeout=self.timeout) as response:
                        response_text = await response.text()
                elif method == "DELETE":
                    async with session.delete(url, timeout=self.timeout) as response:
                        response_text = await response.text()
                else:
                    async with session.get(url, timeout=self.timeout) as response:
                        response_text = await response.text()
                return helper.process_api_response(response_text)
            except aiohttp.ClientConnectionError as err:
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

This modified code now uses `aiohttp` for asynchronous HTTP requests while maintaining the original structure and naming conventions of the code.