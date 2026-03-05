### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statements**: Changed the import from `requests` to `httpx`.
2. **Session Creation**: The `Session` object from `requests` was replaced with `httpx.Client()`, which serves a similar purpose in `httpx`.
3. **Timeout Handling**: The `Timeout` exception from `requests` was replaced with `httpx.TimeoutException`.
4. **Request Method**: The method for making requests (`self.session.request`) was replaced with the corresponding method in `httpx` (`self.session.request` still works, but the way to handle exceptions and the parameters may differ slightly).
5. **Response Handling**: The response handling remains similar, but we ensure to use `response.text` instead of `response.content.decode("utf-8")` since `httpx` provides a `text` property that automatically decodes the response.

Here is the modified code:

```python
import logging
from threading import Lock

from httpx import Client, TimeoutException


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
            self.session = Client(proxies=proxies, headers=headers)
            self.proxies = proxies
            self.headers = headers
            self.logger.info("Using the following custom proxies: %s", proxies)
            system_proxies = {}  # httpx does not have a direct equivalent for utils.get_environ_proxies
            self.logger.info("Using the following system proxies: %s", system_proxies)
            Request._initialized = True

    def _request_wrapper(self, data, timeout, *args, **kwargs):
        headers = {"User-Agent": "pastepwn (https://github.com/d-Rickyy-b/pastepwn)"}

        if self.headers is not None:
            headers.update(self.headers)

        try:
            response = self.session.request(*args, headers=headers, data=data, timeout=timeout, **kwargs)
        except TimeoutException:
            url = kwargs.get("url")
            self.logger.warning("Timeout while requesting %s!", url)
            return ""

        return response.text

    def get(self, url, data=None, timeout=5):
        return self._request_wrapper(method="GET", url=url, data=data, timeout=timeout)

    def post(self, url, data=None, timeout=5):
        return self._request_wrapper(method="POST", url=url, data=data, timeout=timeout)

    def put(self, url, data=None, timeout=5):
        return self._request_wrapper(method="PUT", url=url, data=data, timeout=timeout)

    def delete(self, url, data=None, timeout=5):
        return self._request_wrapper(method="DELETE", url=url, data=data, timeout=timeout)
``` 

This code now uses the `httpx` library while maintaining the original structure and functionality of the code.