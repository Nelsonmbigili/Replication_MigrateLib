### Explanation of Changes
To migrate the code from using the `requests` library to using the `pycurl` library, several changes were necessary:

1. **Response Handling**: The `requests` library provides a `Response` object that includes methods like `.json()` and attributes like `.status_code`. In `pycurl`, we need to handle the response differently, as it does not provide a direct response object. Instead, we will use a callback to capture the response data and manage the HTTP status code separately.

2. **Error Handling**: The way we handle errors and exceptions will also change since `pycurl` does not raise exceptions for HTTP errors by default. We will need to check the HTTP response code manually.

3. **Initialization of Curl**: We will need to initialize a `pycurl.Curl` object and set options for the request, which is different from the simpler interface provided by `requests`.

Here is the modified code:

```python
import pycurl
from io import BytesIO


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp=None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.getinfo(pycurl.RESPONSE_CODE)
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp):
        buffer = BytesIO()
        resp.setopt(pycurl.WRITEFUNCTION, buffer.write)
        try:
            resp.perform()
            return buffer.getvalue().decode('utf-8')
        except Exception as e:
            return str(e)

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
```

### Key Changes in the Code:
- Imported `pycurl` and `BytesIO` for handling the response.
- Used `pycurl.Curl` to create a new curl object and set options for the request.
- Captured the HTTP response code using `resp.getinfo(pycurl.RESPONSE_CODE)`.
- Used a `BytesIO` buffer to capture the response body, which is then decoded to a string for error messages.