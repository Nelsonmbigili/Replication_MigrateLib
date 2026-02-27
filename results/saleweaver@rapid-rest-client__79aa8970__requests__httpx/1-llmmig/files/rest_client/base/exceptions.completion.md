### Explanation of Changes:
1. The `CaseInsensitiveDict` from `requests.structures` is replaced with `httpx.CaseInsensitiveDict`. However, as of `httpx` version 0.28.1, `httpx` does not provide a `CaseInsensitiveDict` directly. To handle this, we need to implement a custom `CaseInsensitiveDict` or use an alternative approach. For simplicity, I will implement a basic custom `CaseInsensitiveDict` that mimics the behavior of the one in `requests`.
2. The rest of the code remains unchanged since the migration only affects the `CaseInsensitiveDict`.

### Modified Code:
```python
from typing import Any


class CaseInsensitiveDict(dict):
    """
    A simple case-insensitive dictionary implementation to replace requests.structures.CaseInsensitiveDict.
    """
    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __delitem__(self, key):
        super().__delitem__(key.lower())

    def __contains__(self, key):
        return super().__contains__(key.lower())

    def get(self, key, default=None):
        return super().get(key.lower(), default)

    def pop(self, key, default=None):
        return super().pop(key.lower(), default)

    def update(self, other=None, **kwargs):
        if other:
            if isinstance(other, dict):
                for key, value in other.items():
                    self[key] = value
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CaseInsensitiveDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass
```

### Key Notes:
- The custom `CaseInsensitiveDict` is implemented to mimic the behavior of `requests.structures.CaseInsensitiveDict`.
- The rest of the code remains unchanged, adhering to the instruction to avoid altering the original coding style or structure.