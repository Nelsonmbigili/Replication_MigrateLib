### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the primary change involves importing the appropriate classes from `requests_futures`. The `requests_futures` library allows for asynchronous requests by using futures, which means we will need to adjust how we handle the response. Specifically, we will import `FuturesSession` from `requests_futures.sessions` instead of using `Response` directly from `requests`. 

In this migration, we will not change the structure of the classes or their methods, but we will ensure that the code is set up to handle future responses correctly.

### Modified Code
```python
from requests_futures.sessions import FuturesSession


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
    def __init__(self, response):
        super().__init__(f'The request made failed with HTTP status code {response.status_code}')
        self.url = response.url
        self.status_code = response.status_code
        self.response = response
```

In this modified code, we have replaced the import statement for `Response` with `FuturesSession` from `requests_futures.sessions`. The `response` parameter in the `NuRequestException` class remains unchanged, as it will still be a response object, but it will now be a future response from the `requests_futures` library.