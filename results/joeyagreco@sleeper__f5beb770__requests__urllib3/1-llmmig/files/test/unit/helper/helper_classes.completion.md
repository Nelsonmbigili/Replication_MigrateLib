### Explanation of Changes:
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. Replaced the import of `HTTPError` from `requests` with `HTTPError` from `urllib3.exceptions`.
2. Updated the `raise_for_status` method to raise `urllib3.exceptions.HTTPError` instead of `requests.exceptions.HTTPError`.

The rest of the code remains unchanged, as the migration only involves replacing the `HTTPError` exception and ensuring compatibility with `urllib3`.

### Modified Code:
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
        https://urllib3.readthedocs.io/en/latest/reference/urllib3.response.html#urllib3.response.HTTPResponse.raise_for_status
        """
        http_error_msg = ""
        if 400 <= self.status_code < 500:
            http_error_msg = f"{self.status_code} Client Error"

        elif 500 <= self.status_code < 600:
            http_error_msg = f"{self.status_code} Server Error"

        if http_error_msg:
            raise HTTPError(http_error_msg)
```