import logging
from threading import Lock
import aiohttp
from aiohttp import ClientTimeout

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
            # Note: aiohttp does not have a direct equivalent for utils.get_environ_proxies
            system_proxies = {}  # Placeholder for system proxies if needed
            self.logger.info("Using the following system proxies: %s", system_proxies)
            Request._initialized = True

    async def _request_wrapper(self, data, timeout, *args, **kwargs):
        headers = {"User-Agent": "pastepwn (https://github.com/d-Rickyy-b/pastepwn)"}

        if self.headers is not None:
            headers.update(self.headers)

        try:
            timeout = ClientTimeout(total=timeout)
            async with self.session.request(*args, headers=headers, proxy=self.proxies, data=data, timeout=timeout, **kwargs) as response:
                return await response.text()
        except aiohttp.ClientTimeout:
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
