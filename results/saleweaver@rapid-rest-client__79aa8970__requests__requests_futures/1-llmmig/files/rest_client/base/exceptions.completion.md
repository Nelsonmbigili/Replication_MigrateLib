### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the following changes were made:
1. The `requests` library is replaced with `requests_futures` in the import statements.
2. Since the `requests_futures` library is built on top of `requests`, it still provides access to `requests.structures.CaseInsensitiveDict`. Therefore, no changes are required for the usage of `CaseInsensitiveDict` in the code.

### Modified Code:
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
```

### Notes:
- The `requests_futures` library is designed to provide asynchronous capabilities by wrapping `requests` in a `FuturesSession`. However, since the provided code does not include any actual HTTP requests, no further changes were necessary.
- If the rest of the application uses synchronous requests, you may need to replace them with asynchronous requests using `FuturesSession`.