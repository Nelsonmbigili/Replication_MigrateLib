### Explanation of Changes:
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Replacement**: Replaced the `requests` import with `httpx`.
2. **HTTP Methods**: Updated the HTTP method calls (`get`, `post`, `put`, `delete`) to use `httpx` equivalents.
3. **Timeout Handling**: `httpx` uses a `timeout` parameter similar to `requests`, so this was directly replaced.
4. **SSL Verification**: `httpx` uses the `verify` parameter for SSL verification, just like `requests`, so this was directly replaced.
5. **Exception Handling**: Replaced `requests.ConnectionError` with `httpx.RequestError`, which is the equivalent exception in `httpx`.

### Modified Code:
```python
"""
SamsungTVWS - Samsung Smart TV WS API wrapper

Copyright (C) 2019 DSR! <xchwarze@gmail.com>

SPDX-License-Identifier: LGPL-3.0
"""

import logging
from typing import Any, Dict, Optional

import httpx

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

    def _rest_request(self, target: str, method: str = "GET") -> Dict[str, Any]:
        url = self._format_rest_url(target)
        try:
            if method == "POST":
                response = httpx.post(url, timeout=self.timeout, verify=False)
            elif method == "PUT":
                response = httpx.put(url, timeout=self.timeout, verify=False)
            elif method == "DELETE":
                response = httpx.delete(url, timeout=self.timeout, verify=False)
            else:
                response = httpx.get(url, timeout=self.timeout, verify=False)
            return helper.process_api_response(response.text)
        except httpx.RequestError as err:
            raise exceptions.HttpApiError(
                "TV unreachable or feature not supported on this model."
            ) from err

    def rest_device_info(self) -> Dict[str, Any]:
        _LOGGING.debug("Get device info via rest api")
        return self._rest_request("")

    def rest_app_status(self, app_id: str) -> Dict[str, Any]:
        _LOGGING.debug("Get app %s status via rest api", app_id)
        return self._rest_request("applications/" + app_id)

    def rest_app_run(self, app_id: str) -> Dict[str, Any]:
        _LOGGING.debug("Run app %s via rest api", app_id)
        return self._rest_request("applications/" + app_id, "POST")

    def rest_app_close(self, app_id: str) -> Dict[str, Any]:
        _LOGGING.debug("Close app %s via rest api", app_id)
        return self._rest_request("applications/" + app_id, "DELETE")

    def rest_app_install(self, app_id: str) -> Dict[str, Any]:
        _LOGGING.debug("Install app %s via rest api", app_id)
        return self._rest_request("applications/" + app_id, "PUT")
```

### Summary of Changes:
- Replaced `requests` with `httpx` for all HTTP requests.
- Updated exception handling to use `httpx.RequestError`.
- Maintained the original structure and logic of the code to ensure compatibility with the rest of the application.