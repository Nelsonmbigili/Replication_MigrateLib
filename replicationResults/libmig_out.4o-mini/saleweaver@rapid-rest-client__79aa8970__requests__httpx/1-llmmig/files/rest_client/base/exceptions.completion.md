### Explanation of Changes
To migrate from the `requests` library to the `httpx` library, the following changes were made:
1. The import statement for `CaseInsensitiveDict` was removed, as `httpx` does not require a separate import for case-insensitive dictionaries. Instead, `httpx` uses standard Python dictionaries which are case-sensitive, but the behavior can be managed as needed.
2. The `requests` library's specific structures and methods were replaced with their `httpx` equivalents where necessary. However, in this case, the original code does not directly use any `requests` methods, so no functional changes were needed in the code itself.

### Modified Code
```python
from typing import Any


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: dict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass
```