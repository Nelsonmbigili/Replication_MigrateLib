### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves replacing the import of `HTTPError` from `requests` with the equivalent import from `requests_futures`. The `requests_futures` library is built on top of `requests` and provides asynchronous capabilities, but it still uses the same `HTTPError` class as `requests`. Therefore, the only change required is to update the import statement.

### Modified Code:
```python
from requests_futures.sessions import FuturesSession
from requests_futures.sessions import HTTPError


class MockResponse:
    def __init__(self, data: dict | list, status_code: int, content: any = None):
        self.__data = data
        self.content = content
        self.status_code = status_code

    def json(self):
        return self.__data

    def raise_for_status(self):
        """
        This is meant to closely resemble the actual raise_for_status method found here:
        https://requests.readthedocs.io/en/latest/_modules/requests/models/#Response.raise_for_status
        """
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Client Error"

        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error"

        if http_error_msg:
            raise HTTPError(http_error_msg, response=self)
```

### Summary of Changes:
1. Replaced `from requests import HTTPError` with `from requests_futures.sessions import HTTPError`.
2. No other changes were made, as the `MockResponse` class and its methods remain compatible with `requests_futures`.