### Explanation of Changes
To migrate the code from using the `requests` library to using the `requests_futures` library, the following changes were made:

1. **Import Change**: The `Session` class from `requests` was replaced with `FuturesSession` from `requests_futures.sessions`.
2. **Session Initialization**: The `Session` object was changed to `FuturesSession`, which allows for asynchronous requests.
3. **Request Handling**: The `_request_wrapper` method was modified to handle the future response returned by `FuturesSession`. Instead of directly accessing the response, we now call `.result()` on the future object to get the actual response.

Here is the modified code:

```python
import logging
from threading import Lock
from requests_futures.sessions import FuturesSession
from requests.exceptions import Timeout


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
            self.session = FuturesSession()  # Changed to FuturesSession
            self.proxies = proxies
            self.headers = headers
            self.logger.info("Using the following custom proxies: %s", proxies)
            system_proxies = utils.get_environ_proxies("https://example.com")
            self.logger.info("Using the following system proxies: %s", system_proxies)
            Request._initialized = True

    def _request_wrapper(self, data, timeout, *args, **kwargs):
        headers = {"User-Agent": "pastepwn (https://github.com/d-Rickyy-b/pastepwn)"}

        if self.headers is not None:
            headers.update(self.headers)

        try:
            future = self.session.request(*args, headers=headers, proxies=self.proxies, data=data, timeout=timeout, **kwargs)
            response = future.result()  # Get the response from the future
        except Timeout:
            url = kwargs.get("url")
            self.logger.warning("Timeout while requesting %s!", url)
            return ""

        return response.content.decode("utf-8")

    def get(self, url, data=None, timeout=5):
        return self._request_wrapper(method="GET", url=url, data=data, timeout=timeout)

    def post(self, url, data=None, timeout=5):
        return self._request_wrapper(method="POST", url=url, data=data, timeout=timeout)

    def put(self, url, data=None, timeout=5):
        return self._request_wrapper(method="PUT", url=url, data=data, timeout=timeout)

    def delete(self, url, data=None, timeout=5):
        return self._request_wrapper(method="DELETE", url=url, data=data, timeout=timeout)
``` 

This code now utilizes the `requests_futures` library for asynchronous HTTP requests while maintaining the original structure and functionality.