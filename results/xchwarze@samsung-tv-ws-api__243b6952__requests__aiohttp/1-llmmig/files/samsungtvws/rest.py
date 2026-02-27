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
