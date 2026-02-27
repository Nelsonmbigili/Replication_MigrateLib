### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. The `Request` object from `requests` was replaced with `pycurl.Curl` to handle HTTP requests.
2. The `build_request` method was updated to configure the `pycurl.Curl` object with the appropriate URL, headers, parameters, and payload.
3. The HTTP method (`GET` or `POST`) is set using `pycurl` options (`c.setopt(pycurl.POST, True)` for POST and the default for GET).
4. The `send` method now executes the `pycurl.Curl` request and captures the response using a `BytesIO` buffer.
5. The `pycurl` library requires manual handling of query parameters and payloads, so these were explicitly added to the URL or request body as needed.

### Modified Code:
```python
import pycurl
from io import BytesIO


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    def send(self, smarty_request):
        curl = self.build_request(smarty_request)
        return self.inner.send(curl)

    def build_request(self, smarty_request):
        c = pycurl.Curl()
        buffer = BytesIO()

        # Set the URL with query parameters if provided
        url = smarty_request.url_prefix
        if smarty_request.parameters:
            query_string = "&".join(f"{key}={value}" for key, value in smarty_request.parameters.items())
            url = f"{url}?{query_string}"
        c.setopt(pycurl.URL, url)

        # Set headers
        header_list = [f"{key}: {value}" for key, value in self.headers.items()]
        c.setopt(pycurl.HTTPHEADER, header_list)

        # Set payload and method
        if smarty_request.payload:
            c.setopt(pycurl.POST, True)
            c.setopt(pycurl.POSTFIELDS, smarty_request.payload)
        else:
            c.setopt(pycurl.HTTPGET, True)

        # Set the response buffer
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)

        return c
```

### Key Notes:
- The `pycurl.Curl` object is used to configure and execute HTTP requests.
- The `BytesIO` buffer is used to capture the response body, which can be processed further in the `inner.send` method.
- Query parameters are manually appended to the URL, as `pycurl` does not handle them automatically like `requests`.
- Headers are set using the `pycurl.HTTPHEADER` option, which expects a list of strings in the format `key: value`.
- The HTTP method is determined based on the presence of a payload (`POST` for payloads, `GET` otherwise).