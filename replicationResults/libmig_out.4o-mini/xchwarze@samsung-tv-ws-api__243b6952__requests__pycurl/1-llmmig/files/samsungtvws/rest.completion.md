### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, the following changes were made:

1. **Importing PycURL**: The `requests` library was replaced with `pycurl`. The `pycurl` library requires a different approach to handle HTTP requests.
2. **Creating a Curl Object**: Instead of using `requests` methods like `get`, `post`, `put`, and `delete`, a `pycurl.Curl` object is created for each request.
3. **Setting Options**: The necessary options for the `Curl` object are set using the `setopt` method, including the URL, HTTP method, and timeout.
4. **Handling Response**: The response is captured using a `BytesIO` object to store the output of the request, which is then converted to a string for processing.
5. **Error Handling**: The error handling for connection issues is adapted to work with `pycurl`.

Here is the modified code:

```python
"""
SamsungTVWS - Samsung Smart TV WS API wrapper

Copyright (C) 2019 DSR! <xchwarze@gmail.com>

SPDX-License-Identifier: LGPL-3.0
"""

import logging
from typing import Any, Dict, Optional
import pycurl
from io import BytesIO

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
        buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(curl.URL, url)
            curl.setopt(curl.WRITEDATA, buffer)
            curl.setopt(curl.TIMEOUT, self.timeout)
            curl.setopt(curl.SSL_VERIFYPEER, False)

            if method == "POST":
                curl.setopt(curl.POST, 1)
            elif method == "PUT":
                curl.setopt(curl.CUSTOMREQUEST, "PUT")
            elif method == "DELETE":
                curl.setopt(curl.CUSTOMREQUEST, "DELETE")

            curl.perform()
            response_body = buffer.getvalue().decode('utf-8')
            return helper.process_api_response(response_body)
        except pycurl.error as err:
            raise exceptions.HttpApiError(
                "TV unreachable or feature not supported on this model."
            ) from err
        finally:
            curl.close()

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

This code now uses `pycurl` for making HTTP requests while maintaining the original structure and functionality of the application.