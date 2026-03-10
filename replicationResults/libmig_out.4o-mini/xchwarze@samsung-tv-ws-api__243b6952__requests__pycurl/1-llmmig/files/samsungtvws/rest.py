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
