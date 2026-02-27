### Explanation of Changes:
The original code uses the `requests` library's `HTTPError` class to simulate HTTP error handling in the `MockResponse` class. Since we are migrating to `pycurl`, which does not have a direct equivalent of `HTTPError`, we need to replace it with a custom exception class to handle HTTP errors. The rest of the `MockResponse` class remains unchanged, as it is a mock implementation and does not directly depend on the `requests` library's functionality.

### Modified Code:
```python
class HTTPError(Exception):
    """
    Custom HTTPError class to replace requests' HTTPError.
    This is used to simulate HTTP error handling in the MockResponse class.
    """
    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response


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

### Key Changes:
1. **Replaced `requests.HTTPError`**:
   - The `requests` library's `HTTPError` class was replaced with a custom `HTTPError` class. This class mimics the behavior of `requests.HTTPError` by accepting an error message and an optional `response` object.

2. **No Changes to `MockResponse` Logic**:
   - The `MockResponse` class remains unchanged except for the replacement of `requests.HTTPError` with the custom `HTTPError` class. This ensures the functionality of the `MockResponse` class is preserved.

This approach ensures the code is migrated to be independent of the `requests` library while maintaining the same behavior.