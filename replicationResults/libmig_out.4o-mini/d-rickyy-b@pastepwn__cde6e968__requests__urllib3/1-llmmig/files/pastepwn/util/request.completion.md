### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, several key changes were made:

1. **Session Management**: The `requests.Session()` was replaced with `urllib3.PoolManager()`, which is the equivalent for managing connections in `urllib3`.
2. **Request Method**: The way requests are made has changed. Instead of using `session.request()`, we now use `http.request()` where `http` is an instance of `PoolManager`.
3. **Timeout Handling**: The `Timeout` exception from `requests` was replaced with `urllib3.exceptions.TimeoutError`.
4. **Response Handling**: The response object from `urllib3` is different from `requests`. The content is accessed via `response.data` instead of `response.content`.

Here is the modified code:

```python
import logging
from threading import Lock
import urllib3
from urllib3.exceptions import TimeoutError

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
            self.http = urllib3.PoolManager()
            self.proxies = proxies
            self.headers = headers
            self.logger.info("Using the following custom proxies: %s", proxies)
            # Note: urllib3 does not have a direct equivalent for get_environ_proxies
            # This line is kept for compatibility but may need to be handled differently
            system_proxies = {}  # Placeholder for system proxies handling
            self.logger.info("Using the following system proxies: %s", system_proxies)
            Request._initialized = True

    def _request_wrapper(self, data, timeout, *args, **kwargs):
        headers = {"User-Agent": "pastepwn (https://github.com/d-Rickyy-b/pastepwn)"}

        if self.headers is not None:
            headers.update(self.headers)

        try:
            response = self.http.request(*args, headers=headers, fields=data, timeout=timeout, **kwargs)
        except TimeoutError:
            url = kwargs.get("url")
            self.logger.warning("Timeout while requesting %s!", url)
            return ""

        return response.data.decode("utf-8")

    def get(self, url, data=None, timeout=5):
        return self._request_wrapper(method="GET", url=url, data=data, timeout=timeout)

    def post(self, url, data=None, timeout=5):
        return self._request_wrapper(method="POST", url=url, data=data, timeout=timeout)

    def put(self, url, data=None, timeout=5):
        return self._request_wrapper(method="PUT", url=url, data=data, timeout=timeout)

    def delete(self, url, data=None, timeout=5):
        return self._request_wrapper(method="DELETE", url=url, data=data, timeout=timeout)
```

### Note
- The handling of system proxies is not directly supported in `urllib3` as it is in `requests`. The line for system proxies is retained as a placeholder, but you may need to implement a custom solution for proxy handling if required.