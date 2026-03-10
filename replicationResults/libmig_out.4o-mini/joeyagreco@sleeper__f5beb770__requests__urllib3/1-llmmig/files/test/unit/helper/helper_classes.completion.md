### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The `HTTPError` class is now imported from `urllib3.exceptions` instead of `requests`.
2. **Error Handling**: The error handling logic remains the same, but the import path for `HTTPError` has been updated to reflect its new location in `urllib3`.

The rest of the code structure and logic remains unchanged to adhere to the guidelines provided.

### Modified Code
```python
from urllib3.exceptions import HTTPError


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
        https://urllib3.readthedocs.io/en/latest/reference/urllib3.exceptions.html#urllib3.exceptions.HTTPError
        """
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Client Error"

        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error"

        if http_error_msg:
            raise HTTPError(http_error_msg, response=self)
```