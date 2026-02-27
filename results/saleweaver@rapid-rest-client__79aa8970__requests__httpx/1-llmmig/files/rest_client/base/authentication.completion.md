### Explanation of Changes:
To migrate the code from `requests` to `httpx`, the following changes were made:
1. The `AuthBase` class from `requests` was replaced with `httpx.Auth` as `httpx` uses a different base class for custom authentication.
2. The `__call__` method in the `BearerTokenAuth` class was replaced with the `auth_flow` method, which is the required method for implementing custom authentication in `httpx`. This method is a generator that yields the request object after modifying it.

### Modified Code:
```python
from httpx import Auth


class Authentication(Auth):
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    def auth_flow(self, request):
        request.headers['Authorization'] = f'{self.type} {self.token}'
        yield request
```