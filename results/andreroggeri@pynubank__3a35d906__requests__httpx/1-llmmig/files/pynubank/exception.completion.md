### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. The `Response` class from `requests` was replaced with the `Response` class from `httpx`.
2. The import statement was updated to import `Response` from `httpx` instead of `requests`.

No other changes were made, as the functionality and usage of the `Response` object in this code remain the same between the two libraries.

### Modified Code
```python
from httpx import Response


class NuException(Exception):

    def __init__(self, message):
        super().__init__(message)


class NuInvalidAuthenticationMethod(NuException):
    def __init__(self, message):
        super().__init__(message)


class NuMissingCreditCard(NuException):
    def __init__(self):
        super().__init__(f'Couldn\'t fetch bills due to missing credit card.')


class NuRequestException(NuException):
    def __init__(self, response: Response):
        super().__init__(f'The request made failed with HTTP status code {response.status_code}')
        self.url = response.url
        self.status_code = response.status_code
        self.response = response
```