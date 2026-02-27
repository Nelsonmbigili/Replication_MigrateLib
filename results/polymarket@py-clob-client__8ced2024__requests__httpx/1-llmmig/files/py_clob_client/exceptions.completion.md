### Explanation of Changes:
To migrate the code from using the `requests` library to `httpx`, the following changes were made:
1. Replaced the `requests.Response` type hint with `httpx.Response` in the `PolyApiException` class.
2. Updated the `_get_message` method to handle `httpx.Response` objects instead of `requests.Response`. The `httpx.Response` API is similar to `requests.Response`, so no significant changes were required for accessing `.json()` or `.text`.

### Modified Code:
```python
from httpx import Response


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp: Response = None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.status_code
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp: Response):
        try:
            return resp.json()
        except Exception:
            return resp.text

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
```

### Summary of Changes:
- Replaced `from requests import Response` with `from httpx import Response`.
- Updated type hints and method logic to work with `httpx.Response`. The behavior of `.json()` and `.text` remains the same between `requests` and `httpx`, so no additional changes were necessary.