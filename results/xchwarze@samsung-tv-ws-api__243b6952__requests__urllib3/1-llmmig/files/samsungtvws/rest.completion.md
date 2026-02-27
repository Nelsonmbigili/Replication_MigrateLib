### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Import Replacement**: Removed the `requests` import and replaced it with `urllib3`.
2. **HTTP Request Handling**: Replaced `requests.get`, `requests.post`, `requests.put`, and `requests.delete` with the equivalent methods from `urllib3.PoolManager`.
   - `urllib3.PoolManager` is used to manage HTTP connections.
   - The `timeout` parameter is passed using `urllib3.util.Timeout`.
   - The `verify=False` functionality in `requests` is replaced by setting `cert_reqs='CERT_NONE'` in `urllib3.PoolManager` to disable SSL certificate verification.
3. **Error Handling**: Replaced `requests.ConnectionError` with `urllib3.exceptions.HTTPError` for handling connection-related exceptions.
4. **Response Handling**: Adjusted the way the response body is accessed. In `urllib3`, the response body is accessed via `response.data.decode("utf-8")` instead of `response.text`.

### Modified Code
```python
"""
SamsungTVWS - Samsung Smart TV WS API wrapper

Copyright (C) 2019 DSR! <xchwarze@gmail.com>

SPDX-License-Identifier: LGPL-3.0
"""

import logging
from typing import Any, Dict, Optional

import urllib3
from urllib3.exceptions import HTTPError
from urllib3.util import Timeout

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
        self.http = urllib3.PoolManager(cert_reqs='CERT_NONE')  # Disable SSL verification

    def _rest_request(self, target: str, method: str = "GET") -> Dict[str, Any]:
        url = self._format_rest_url(target)
        try:
            if method == "POST":
                response = self.http.request(
                    "POST", url, timeout=Timeout(connect=self.timeout, read=self.timeout)
                )
            elif method == "PUT":
                response = self.http.request(
                    "PUT", url, timeout=Timeout(connect=self.timeout, read=self.timeout)
                )
            elif method == "DELETE":
                response = self.http.request(
                    "DELETE", url, timeout=Timeout(connect=self.timeout, read=self.timeout)
                )
            else:
                response = self.http.request(
                    "GET", url, timeout=Timeout(connect=self.timeout, read=self.timeout)
                )
            return helper.process_api_response(response.data.decode("utf-8"))
        except HTTPError as err:
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

### Key Notes
- The `urllib3.PoolManager` is used to manage HTTP connections, and SSL verification is disabled by setting `cert_reqs='CERT_NONE'`.
- The `timeout` parameter is handled using `urllib3.util.Timeout` to specify both connection and read timeouts.
- The response body is decoded using `response.data.decode("utf-8")` to match the behavior of `requests.response.text`.
- The `urllib3.exceptions.HTTPError` is used to handle connection-related errors, replacing `requests.ConnectionError`.