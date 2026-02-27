### Explanation of Changes:
The provided code does not directly use any functionality from the `requests` library other than importing `CaseInsensitiveDict`. Since `pycurl` does not have an equivalent for `CaseInsensitiveDict`, we need to replace it with a custom implementation or use an alternative from Python's standard library. In this case, we will use `collections.abc.Mapping` to create a simple case-insensitive dictionary.

### Modified Code:
```python
from typing import Any
from collections.abc import Mapping


class CaseInsensitiveDict(Mapping):
    """
    A simple case-insensitive dictionary implementation to replace
    requests.structures.CaseInsensitiveDict.
    """
    def __init__(self, data=None, **kwargs):
        self._store = {}
        if data:
            self.update(data)
        if kwargs:
            self.update(kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (original_key for original_key, _ in self._store.values())

    def __len__(self):
        return len(self._store)

    def __contains__(self, key):
        return key.lower() in self._store

    def update(self, other=None, **kwargs):
        if other:
            if hasattr(other, "keys"):
                for key in other.keys():
                    self[key] = other[key]
            else:
                for key, value in other:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def get(self, key, default=None):
        return self._store.get(key.lower(), (None, default))[1]

    def items(self):
        return ((original_key, value) for original_key, value in self._store.values())

    def keys(self):
        return (original_key for original_key, _ in self._store.values())

    def values(self):
        return (value for _, value in self._store.values())

    def __repr__(self):
        return str(dict(self.items()))


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CaseInsensitiveDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass
```

### Key Changes:
1. **Replaced `requests.structures.CaseInsensitiveDict`**:
   - Since `pycurl` does not provide a `CaseInsensitiveDict` equivalent, I implemented a custom `CaseInsensitiveDict` class using Python's `collections.abc.Mapping`.
   - This class mimics the behavior of `requests.structures.CaseInsensitiveDict`, ensuring case-insensitive key handling while preserving the original key casing for representation.

2. **Updated Imports**:
   - Removed the import of `requests.structures.CaseInsensitiveDict` since it is no longer used.
   - Added `collections.abc.Mapping` to implement the custom `CaseInsensitiveDict`.

The rest of the code remains unchanged, as it does not directly depend on the `requests` library.