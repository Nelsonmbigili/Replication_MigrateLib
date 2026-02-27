### Explanation of Changes:
To migrate from the `requests` library to `aiohttp`, the following changes were made:
1. Replaced the `requests.structures.CaseInsensitiveDict` with `aiohttp.CIMultiDict`, which serves a similar purpose for case-insensitive headers in `aiohttp`.
2. Updated the import statement to use `aiohttp.CIMultiDict` instead of `requests.structures.CaseInsensitiveDict`.

No other changes were necessary since the provided code does not include any HTTP request logic or other `requests`-specific functionality.

### Modified Code:
```python
from typing import Any

from aiohttp import CIMultiDict


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CIMultiDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass
```