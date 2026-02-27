### Explanation of Changes:
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. Replaced the `requests.Response` type hint with `urllib3.response.HTTPResponse` since `urllib3` uses `HTTPResponse` objects instead of `Response`.
2. Updated the `_get_message` method to handle `urllib3.response.HTTPResponse` objects. Unlike `requests.Response`, `HTTPResponse` does not have a `json()` method, so we need to manually decode the response body and parse it as JSON.
3. Adjusted the handling of the response body in `_get_message` to ensure compatibility with `urllib3`. The response body in `HTTPResponse` is a byte stream, so it must be decoded before processing.

### Modified Code:
```python
from urllib3.response import HTTPResponse
import json


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp: HTTPResponse = None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.status
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp: HTTPResponse):
        try:
            # Read and decode the response body
            body = resp.data.decode('utf-8')
            # Attempt to parse the body as JSON
            return json.loads(body)
        except json.JSONDecodeError:
            # If parsing fails, return the raw text
            return body

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
```

### Key Points:
- The `requests.Response` type hint was replaced with `urllib3.response.HTTPResponse`.
- The `json()` method from `requests.Response` was replaced with manual decoding and JSON parsing using `json.loads()`.
- The response body in `HTTPResponse` is accessed via `resp.data` and must be decoded from bytes to a string before processing.