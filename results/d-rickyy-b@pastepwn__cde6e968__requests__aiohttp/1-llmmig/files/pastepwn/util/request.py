import logging
from threading import Lock
import aiohttp
from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientError


class Request:
    _instance = None
    _initialized = False
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        # override method to implement singleton
        # source: http://alacret.blogspot.com/2015/04/python-thread-safe-singleton-pattern.html
        if Request._instance is None:
            with Request._lock:
                if Request._instance is None:
                    Request._instance = super().__new__(cls)
        return Request._instance

    def __init__(self, proxies=None, headers=None):
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.session = aiohttp.ClientSession()
            self.proxies = proxies
            self.headers = headers
            self.logger.info("Using the following custom proxies: %s", proxies)
            Request._initialized = True

    async def _request_wrapper(self, data, timeout, *args, **kwargs):
        headers = {"User-Agent": "pastepwn (https://github.com/d-Rickyy-b/pastepwn)"}

        if self.headers is not None:
            headers.update(self.headers)

        # aiohttp uses a different format for proxies
        proxy = self.proxies.get("https") if self.proxies else None

        try:
            async with self.session.request(*args, headers=headers, proxy=proxy, data=data, timeout=ClientTimeout(total=timeout), **kwargs) as response:
                return await response.text()
        except ClientError as e:
            url = kwargs.get("url")
            self.logger.warning("Error while requesting %s: %s", url, str(e))
            return ""
        except asyncio.TimeoutError:
            url = kwargs.get("url")
            self.logger.warning("Timeout while requesting %s!", url)
            return ""

    async def get(self, url, data=None, timeout=5):
        return await self._request_wrapper(method="GET", url=url, data=data, timeout=timeout)

    async def post(self, url, data=None, timeout=5):
        return await self._request_wrapper(method="POST", url=url, data=data, timeout=timeout)

    async def put(self, url, data=None, timeout=5):
        return await self._request_wrapper(method="PUT", url=url, data=data, timeout=timeout)

    async def delete(self, url, data=None, timeout=5):
        return await self._request_wrapper(method="DELETE", url=url, data=data, timeout=timeout)

    async def close(self):
        """Close the aiohttp session."""
        await self.session.close()
