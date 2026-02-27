### Explanation of Changes:
1. The `CaseInsensitiveDict` from the `requests.structures` module is replaced with `urllib3.util.headers.HTTPHeaderDict`, which serves a similar purpose in `urllib3` for handling case-insensitive headers.
2. The import statement for `CaseInsensitiveDict` from `requests` is removed and replaced with the appropriate import for `HTTPHeaderDict` from `urllib3`.

### Modified Code:
```python
from typing import Any

from urllib3.util.headers import HTTPHeaderDict


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: HTTPHeaderDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass
```