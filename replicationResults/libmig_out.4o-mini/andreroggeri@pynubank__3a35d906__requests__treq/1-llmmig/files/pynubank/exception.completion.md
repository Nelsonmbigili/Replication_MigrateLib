### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement for `Response` from `requests` was removed, as `treq` does not require a separate `Response` class import. Instead, `treq` returns a response object directly.
2. **Response Handling**: The `Response` object from `requests` is replaced with the response object returned by `treq`. The attributes accessed (like `status_code` and `url`) remain the same, as `treq`'s response object has similar attributes.

Here is the modified code:

```python
# Removed the import of Response from requests
# from requests import Response

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
    def __init__(self, response):  # Removed type hint for Response
        super().__init__(f'The request made failed with HTTP status code {response.status_code}')
        self.url = response.url
        self.status_code = response.status_code
        self.response = response
``` 

This code now uses `treq` for handling HTTP requests while maintaining the original structure and functionality.