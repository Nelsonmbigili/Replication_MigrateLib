### Explanation of Changes
To migrate from the `requests` library to the `treq` library, the following changes were made:
1. The import statement for `requests` was removed since it is no longer needed.
2. The `CaseInsensitiveDict` from `requests.structures` was replaced with `treq`'s equivalent, which is `treq.CaseInsensitiveDict`. This is necessary to maintain the same functionality for handling case-insensitive headers.

### Modified Code
```python
from typing import Any

from treq import CaseInsensitiveDict


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CaseInsensitiveDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass
```