import logging
from threading import Lock
import pycurl
from io import BytesIO

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
            self.proxies = proxies
            self.headers = headers
            self.logger.info("Using the following custom proxies: %s", proxies)
            Request._initialized = True

    def _request_wrapper(self, data, timeout, *args, **kwargs):
        headers = ["User-Agent: pastepwn (https://github.com/d-Rickyy-b/pastepwn)"]

        if self.headers is not None:
            headers.extend(f"{key}: {value}" for key, value in self.headers.items())

        response_buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, kwargs.get("url"))
        curl.setopt(curl.WRITEDATA, response_buffer)
        curl.setopt(curl.HTTPHEADER, headers)
        if self.proxies:
            curl.setopt(curl.PROXY, self.proxies)
        curl.setopt(curl.TIMEOUT, timeout)

        try:
            curl.perform()
        except pycurl.error as e:
            url = kwargs.get("url")
            self.logger.warning("Timeout while requesting %s! Error: %s", url, e)
            return ""

        curl.close()
        return response_buffer.getvalue().decode("utf-8")

    def get(self, url, data=None, timeout=5):
        return self._request_wrapper(method="GET", url=url, data=data, timeout=timeout)

    def post(self, url, data=None, timeout=5):
        return self._request_wrapper(method="POST", url=url, data=data, timeout=timeout)

    def put(self, url, data=None, timeout=5):
        return self._request_wrapper(method="PUT", url=url, data=data, timeout=timeout)

    def delete(self, url, data=None, timeout=5):
        return self._request_wrapper(method="DELETE", url=url, data=data, timeout=timeout)
