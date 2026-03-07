### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: The import statement for `HTTPError` was changed to import from `httpx` instead of `requests`.
2. **Error Handling**: The `raise_for_status` method was modified to raise `httpx.HTTPStatusError` instead of `requests.HTTPError`. This is because `httpx` has its own error handling class for HTTP errors.

The rest of the code remains unchanged to adhere to the guidelines provided.

### Modified Code
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
        https://httpx.readthedocs.io/en/latest/#httpx.Response.raise_for_status
        """
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Client Error"

        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error"

        if http_error_msg:
            raise HTTPStatusError(http_error_msg, response=self)
```