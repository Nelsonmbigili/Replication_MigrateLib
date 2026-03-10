### Explanation of Changes
To migrate the code from using the `requests` library to using `urllib3`, the following changes were made:

1. **Import Statements**: The import statement for `CaseInsensitiveDict` was removed since `urllib3` does not have a direct equivalent. Instead, we can use a standard Python dictionary for headers, as `urllib3` handles headers in a case-insensitive manner by default.
2. **Exception Handling**: The `ApiException` class remains largely unchanged, but we will not use `CaseInsensitiveDict` for headers anymore.

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