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
        buffer = BytesIO()  # Buffer to capture the response body
        curl = pycurl.Curl()

        try:
            # Set the URL and common options
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            curl.setopt(pycurl.TIMEOUT, int(self.timeout) if self.timeout else 0)
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)  # Disable SSL verification
            curl.setopt(pycurl.SSL_VERIFYHOST, 0)

            # Set the HTTP method
            if method == "POST":
                curl.setopt(pycurl.POST, 1)
            elif method == "PUT":
                curl.setopt(pycurl.CUSTOMREQUEST, "PUT")
            elif method == "DELETE":
                curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")
            else:  # Default to GET
                curl.setopt(pycurl.HTTPGET, 1)

            # Perform the request
            curl.perform()

            # Decode the response body
            response_body = buffer.getvalue().decode("utf-8")
            return helper.process_api_response(response_body)

        except pycurl.error as err:
            raise exceptions.HttpApiError(
                "TV unreachable or feature not supported on this model."
            ) from err

        finally:
            # Clean up resources
            curl.close()
            buffer.close()

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
