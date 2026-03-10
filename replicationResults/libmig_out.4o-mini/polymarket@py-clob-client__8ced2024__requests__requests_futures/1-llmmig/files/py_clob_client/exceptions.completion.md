### Explanation of Changes
To migrate the code from using the `requests` library to using the `requests_futures` library, the primary change involves importing the appropriate classes from `requests_futures`. The `requests_futures` library allows for asynchronous requests by using a `FuturesSession` instead of the standard `Session` from `requests`. In this case, we will replace the import statement for `Response` with the necessary import from `requests_futures`. However, since the original code does not directly create or use a `Response` object, we will keep the usage of `Response` intact, as it is still relevant for handling responses in the context of exceptions.

### Modified Code
```python
from requests_futures.sessions import FuturesSession


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp: FuturesSession = None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.status_code
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp: FuturesSession):
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

In this modified code, the import statement has been changed to import `FuturesSession` from `requests_futures.sessions`. The type hint for the `resp` parameter in the `PolyApiException` class has also been updated to reflect that it can be a `FuturesSession`. The rest of the code remains unchanged to adhere to the guidelines provided.