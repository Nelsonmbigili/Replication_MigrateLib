### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Session Replacement**: The `requests.Session` object was removed, as `pycurl` does not use session objects. Instead, a `pycurl.Curl` object is created for each request.
2. **Request Handling**: The `session.request` method was replaced with `pycurl`'s configuration and execution methods. This involves setting options on the `pycurl.Curl` object (e.g., URL, HTTP method, headers, proxies, etc.).
3. **Timeout Handling**: `pycurl` uses specific options (`pycurl.CONNECTTIMEOUT` and `pycurl.TIMEOUT`) to handle timeouts.
4. **Response Handling**: `pycurl` writes the response data to a buffer (e.g., `io.BytesIO`) instead of returning it directly. The buffer content is then decoded to a string.
5. **Error Handling**: `pycurl` raises exceptions for errors, so the `Timeout` exception from `requests` was replaced with `pycurl.error`.
6. **Proxies**: Proxy settings were configured using `pycurl.PROXY` and related options.
7. **Headers**: Headers were set using `pycurl.HTTPHEADER`.

Below is the modified code.

---

### Modified Code
```python
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
```

---

### Key Notes
1. **Proxy Configuration**: The proxy configuration assumes a simple dictionary with keys like `"http"`. If the proxy format differs, additional adjustments may be needed.
2. **Error Handling**: `pycurl.error` is a generic exception, so specific error codes (e.g., timeouts) can be handled if needed.
3. **Headers**: Headers are converted to a list of strings in the format `"Key: Value"`, as required by `pycurl`.
4. **Response Buffer**: The response is written to an `io.BytesIO` buffer and then decoded to a string. This mimics the behavior of `requests`'s `response.content.decode("utf-8")`.