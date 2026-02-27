### Explanation of Changes:
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Session Replacement**: Replaced `requests.Session` with `httpx.Client`, which serves a similar purpose in `httpx`.
2. **Proxies Handling**: Updated the `proxies` parameter to match `httpx`'s format. In `httpx`, proxies are passed as a dictionary with keys like `"http"` and `"https"`.
3. **Timeout Handling**: Updated the `Timeout` exception to `httpx.TimeoutException`, which is the equivalent in `httpx`.
4. **Request Method**: Replaced `session.request` with `client.request`, which is the equivalent in `httpx`.
5. **Response Decoding**: Updated `response.content.decode("utf-8")` to `response.text`, as `httpx` provides the decoded text directly via the `text` attribute.
6. **Environment Proxies**: The `httpx` library automatically handles environment proxies, so no changes were needed for `utils.get_environ_proxies`.

### Modified Code:
```python
import logging
from threading import Lock

import httpx
from httpx import TimeoutException


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
            self.client = httpx.Client(proxies=proxies)
            self.proxies = proxies
            self.headers = headers
            self.logger.info("Using the following custom proxies: %s", proxies)
            system_proxies = httpx.utils.get_environ_proxies("https://example.com")
            self.logger.info("Using the following system proxies: %s", system_proxies)
            Request._initialized = True

    def _request_wrapper(self, data, timeout, *args, **kwargs):
        headers = {"User-Agent": "pastepwn (https://github.com/d-Rickyy-b/pastepwn)"}

        if self.headers is not None:
            headers.update(self.headers)

        try:
            response = self.client.request(*args, headers=headers, data=data, timeout=timeout, **kwargs)
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

### Key Notes:
- The `httpx.Client` is used as a replacement for `requests.Session` to maintain persistent connections and session-level configurations.
- The `httpx` library automatically handles environment proxies, so the `utils.get_environ_proxies` call remains unchanged.
- The `TimeoutException` from `httpx` is used to handle timeout errors.
- The `response.text` attribute in `httpx` is used to directly access the decoded response content.