### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves replacing the `Response` class from `requests` with the equivalent `Response` class from `requests_futures`. Since `requests_futures` is built on top of `requests`, it uses the same `Response` class, so no additional changes are required in this specific code snippet. However, the import statement must be updated to import `Response` from `requests_futures`.

### Modified Code:
```python
from requests_futures.sessions import FuturesSession
from requests_futures.sessions import Response


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

### Key Changes:
1. Replaced `from requests import Response` with `from requests_futures.sessions import Response`.
2. No other changes were necessary because `requests_futures` is an extension of `requests`, and the `Response` class remains compatible.