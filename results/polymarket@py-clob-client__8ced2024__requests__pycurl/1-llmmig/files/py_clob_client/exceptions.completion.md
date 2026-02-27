### Explanation of Changes:
The original code uses the `requests` library to handle HTTP responses (`Response` objects). To migrate to `pycurl`, the following changes were made:
1. Removed the import of `Response` from `requests` since it is no longer used.
2. Updated the `PolyApiException` class to handle raw HTTP responses using `pycurl`. In `pycurl`, responses are typically captured as raw byte strings, so additional handling is required to parse the response body and status code.
3. Added a helper function `_parse_pycurl_response` to simulate the behavior of `requests.Response` by extracting the status code and response body from `pycurl`'s output.
4. Updated the `_get_message` method to handle raw response data (byte strings) instead of `requests.Response` objects.

### Modified Code:
```python
import json
import pycurl
from io import BytesIO


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp=None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code, self.response_body = self._parse_pycurl_response(resp)
            self.error_msg = self._get_message(self.response_body)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _parse_pycurl_response(self, resp):
        """
        Parses the raw response from pycurl and extracts the status code and body.
        :param resp: A tuple containing (status_code, response_body) from pycurl.
        :return: A tuple (status_code, response_body).
        """
        status_code, response_body = resp
        return status_code, response_body

    def _get_message(self, response_body):
        """
        Extracts the error message from the response body.
        :param response_body: The raw response body (bytes).
        :return: Parsed JSON or plain text message.
        """
        try:
            return json.loads(response_body)
        except Exception:
            return response_body.decode('utf-8')

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
```

### Key Notes:
1. **`pycurl` Response Handling**: Unlike `requests`, `pycurl` does not provide a high-level `Response` object. Instead, you must manually capture the response body and status code. This is why the `_parse_pycurl_response` method was added.
2. **Raw Byte Strings**: `pycurl` returns raw byte strings for the response body, so decoding and JSON parsing are handled explicitly in `_get_message`.
3. **Backward Compatibility**: The class structure and method names remain unchanged to ensure compatibility with the rest of the application.