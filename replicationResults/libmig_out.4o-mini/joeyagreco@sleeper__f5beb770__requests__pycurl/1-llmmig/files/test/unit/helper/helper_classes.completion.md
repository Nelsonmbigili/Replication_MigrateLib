### Explanation of Changes
To migrate the code from using the `requests` library to using `pycurl`, the following changes were made:

1. **Import Statement**: The import statement for `HTTPError` was removed since `pycurl` does not have a direct equivalent for this exception. Instead, error handling will be done using `pycurl.error`.
2. **MockResponse Class**: The `MockResponse` class remains largely unchanged, but the `raise_for_status` method will be modified to handle errors that may arise from `pycurl`.
3. **Error Handling**: The error handling in `raise_for_status` was adapted to raise a `pycurl.error` instead of `HTTPError`, as `pycurl` does not have a built-in mechanism for HTTP status codes like `requests`.

Here is the modified code:

```python
import pycurl

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
            raise pycurl.error(http_error_msg)
``` 

This code now uses `pycurl` for error handling while maintaining the structure and functionality of the original `requests`-based implementation.