### Explanation of Changes:
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. Replaced the import of `HTTPError` from `requests` with `HTTPStatusError` from `httpx`, as `httpx` uses `HTTPStatusError` for handling HTTP errors.
2. Updated the `raise_for_status` method to raise `httpx.HTTPStatusError` instead of `requests.HTTPError`. The `httpx.HTTPStatusError` constructor requires a `request` object and a `response` object, so I added placeholders (`None`) for the `request` object since the `MockResponse` class does not simulate a full HTTP request.

### Modified Code:
```python
from httpx import HTTPStatusError


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
        https://www.python-httpx.org/api/#httpx.Response.raise_for_status
        """
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Client Error"

        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error"

        if http_error_msg:
            # httpx.HTTPStatusError requires a request and response object; using None for request
            raise HTTPStatusError(http_error_msg, request=None, response=self)
```