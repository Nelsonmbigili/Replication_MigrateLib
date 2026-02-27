import logging
from threading import Lock
import pycurl
import io


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
            # Note: pycurl does not have a direct equivalent for `utils.get_environ_proxies`
            self.logger.info("Using the following system proxies: %s", proxies)
            Request._initialized = True

    def _request_wrapper(self, data, timeout, method, url, *args, **kwargs):
        headers = ["User-Agent: pastepwn (https://github.com/d-Rickyy-b/pastepwn)"]

        if self.headers is not None:
            headers.extend([f"{key}: {value}" for key, value in self.headers.items()])

        buffer = io.BytesIO()
        curl = pycurl.Curl()

        try:
            # Set URL and method
            curl.setopt(pycurl.URL, url)
            if method == "POST":
                curl.setopt(pycurl.POST, 1)
                if data:
                    curl.setopt(pycurl.POSTFIELDS, data)
            elif method == "PUT":
                curl.setopt(pycurl.CUSTOMREQUEST, "PUT")
                if data:
                    curl.setopt(pycurl.POSTFIELDS, data)
            elif method == "DELETE":
                curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")
            elif method == "GET":
                curl.setopt(pycurl.HTTPGET, 1)

            # Set headers
            curl.setopt(pycurl.HTTPHEADER, headers)

            # Set timeout
            curl.setopt(pycurl.CONNECTTIMEOUT, timeout)
            curl.setopt(pycurl.TIMEOUT, timeout)

            # Set proxy if provided
            if self.proxies:
                curl.setopt(pycurl.PROXY, self.proxies.get("http", ""))
                curl.setopt(pycurl.PROXYPORT, 8080)  # Default proxy port

            # Write response to buffer
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

            # Perform the request
            curl.perform()

        except pycurl.error as e:
            self.logger.warning("Error while requesting %s: %s", url, e)
            return ""

        finally:
            curl.close()

        # Decode response
        return buffer.getvalue().decode("utf-8")

    def get(self, url, data=None, timeout=5):
        return self._request_wrapper(method="GET", url=url, data=data, timeout=timeout)

    def post(self, url, data=None, timeout=5):
        return self._request_wrapper(method="POST", url=url, data=data, timeout=timeout)

    def put(self, url, data=None, timeout=5):
        return self._request_wrapper(method="PUT", url=url, data=data, timeout=timeout)

    def delete(self, url, data=None, timeout=5):
        return self._request_wrapper(method="DELETE", url=url, data=data, timeout=timeout)
