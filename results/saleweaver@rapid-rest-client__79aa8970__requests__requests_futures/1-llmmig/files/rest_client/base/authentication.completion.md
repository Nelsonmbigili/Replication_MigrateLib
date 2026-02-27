### Explanation of the Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves importing the `requests_futures` library instead of `requests`. Since the provided code does not directly use any synchronous request methods (e.g., `requests.get`, `requests.post`), no further changes are required to adapt the code for `requests_futures`. The `AuthBase` class is still available in `requests_futures` because it is built on top of `requests`.

### Modified Code:
```python
from requests_futures.sessions import FuturesSession
from requests.auth import AuthBase


class Authentication(AuthBase):
    pass


class BearerTokenAuth(Authentication):
    def __init__(self, token, _type='Bearer'):
        self.token = token
        self.type = _type

    def __call__(self, r):
        r.headers['Authorization'] = f'{self.type} {self.token}'
        return r
```

### Key Notes:
1. The `requests_futures` library is built on top of `requests`, so the `AuthBase` class and its functionality remain unchanged.
2. No additional changes were necessary because the provided code does not include any synchronous request calls that would need to be replaced with asynchronous ones using `FuturesSession`.