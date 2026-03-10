### Explanation of Changes
To migrate from the `requests` library to the `requests_futures` library, we need to adjust how we handle requests. The `requests_futures` library allows for asynchronous requests by using futures. This means we will need to import `FuturesSession` from `requests_futures.sessions` instead of using the standard `requests` session. However, since the provided code does not include any actual request calls, we will only modify the import statement to reflect the use of `FuturesSession`. The rest of the code remains unchanged as it defines authentication classes.

### Modified Code
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