### Explanation of Changes
To migrate from the `requests` library to the `requests_futures` library, the primary change involves replacing the synchronous request calls with asynchronous ones provided by `requests_futures`. This allows for non-blocking HTTP requests, which can improve performance in applications that make multiple requests. The `requests_futures` library provides a `FuturesSession` class that extends the standard `requests.Session` to support asynchronous requests.

In the provided code, there are no direct HTTP requests being made, so the migration will focus on importing the `FuturesSession` and using it in place of the standard `requests` session. However, since the original code does not include any request logic, the migration will be minimal and will only demonstrate how to set up the `FuturesSession`.

### Modified Code
```python
from typing import Any
from requests_futures.sessions import FuturesSession
from requests.structures import CaseInsensitiveDict


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CaseInsensitiveDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass

# Example of how to use FuturesSession (not part of the original code)
session = FuturesSession()
# You can now use session to make asynchronous requests
# response_future = session.get('http://example.com')
``` 

In this modified code, I imported `FuturesSession` from `requests_futures.sessions` and provided a comment on how to use it for making asynchronous requests. The rest of the code remains unchanged as per your instructions.