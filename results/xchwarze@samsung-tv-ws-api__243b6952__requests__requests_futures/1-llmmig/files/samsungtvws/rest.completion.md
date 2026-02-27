### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Request Methods**: Updated the request methods (`get`, `post`, `put`, `delete`) to use the `FuturesSession` instance.
4. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is called to get the actual response synchronously (to maintain the original synchronous behavior).

### Modified Code:
```python
"""
SamsungTVWS - Samsung Smart TV WS API wrapper

Copyright (C) 2019 DSR! <xchwarze@gmail.com>

SPDX-License-Identifier: LGPL-3.0
"""

import logging
from typing import Any, Dict, Optional

from requests_futures.sessions import FuturesSession

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
        self.session = FuturesSession()

    def _rest_request(self, target: str, method: str = "GET") -> Dict[str, Any]:
        url = self._format_rest_url(target)
        try:
            if method == "POST":
                future = self.session.post(url, timeout=self.timeout, verify=False)
            elif method == "PUT":
                future = self.session.put(url, timeout=self.timeout, verify=False)
            elif method == "DELETE":
                future = self.session.delete(url, timeout=self.timeout, verify=False)
            else:
                future = self.session.get(url, timeout=self.timeout, verify=False)
            
            # Wait for the response and process it
            response = future.result()
            return helper.process_api_response(response.text)
        except Exception as err:
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

### Key Points:
- The `FuturesSession` class from `requests_futures` is used to handle asynchronous requests.
- The `.result()` method is called on the `Future` object to block and retrieve the response, ensuring the behavior remains synchronous as in the original code.
- No other parts of the code were modified to maintain compatibility with the rest of the application.