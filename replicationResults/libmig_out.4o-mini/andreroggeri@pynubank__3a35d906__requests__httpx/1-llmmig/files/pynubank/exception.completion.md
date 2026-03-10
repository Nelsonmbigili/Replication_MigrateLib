### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: The import statement for `Response` was changed from `requests` to `httpx`.
2. **Response Handling**: The `Response` object from `httpx` is used in the same way as in `requests`, so no changes were needed in how the `Response` object is utilized in the `NuRequestException` class.

The overall structure and logic of the code remain unchanged, adhering to the instruction not to refactor or alter the original coding style.

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