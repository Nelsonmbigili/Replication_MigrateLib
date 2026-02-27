### Explanation of Changes:
1. The `requests.structures.CaseInsensitiveDict` is replaced with `treq`'s equivalent, which is `treq.client.CaseInsensitiveDict`. However, `treq` does not provide a direct equivalent for `CaseInsensitiveDict`. Instead, you can use Python's `collections.abc.Mapping` or implement a custom case-insensitive dictionary if needed. For simplicity, I will use `requests.structures.CaseInsensitiveDict` directly, as `treq` does not natively provide this functionality.
2. Since the provided code does not include any actual HTTP requests or responses, no further changes are required for the migration.

### Modified Code:
```python
from typing import Any

from requests.structures import CaseInsensitiveDict  # Retained as treq does not provide an equivalent


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CaseInsensitiveDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass
```

### Notes:
- Since the provided code does not include any actual HTTP requests or responses, no further migration to `treq` was necessary.
- The `CaseInsensitiveDict` from `requests` is retained because `treq` does not provide a direct equivalent. If you need a custom implementation, you can create one, but that is outside the scope of this migration.