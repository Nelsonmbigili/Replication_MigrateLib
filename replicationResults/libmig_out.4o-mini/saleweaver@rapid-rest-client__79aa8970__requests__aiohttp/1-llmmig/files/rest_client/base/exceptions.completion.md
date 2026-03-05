### Explanation of Changes
To migrate from the `requests` library to the `aiohttp` library, the following changes were made:

1. **Importing aiohttp**: The `aiohttp` library is imported to handle asynchronous HTTP requests.
2. **Asynchronous Context**: The code will need to be adapted to use asynchronous functions and context managers, as `aiohttp` is designed for asynchronous operations.
3. **Session Management**: Instead of using `requests.get()` or `requests.post()`, we will use `aiohttp.ClientSession()` to manage HTTP sessions.
4. **Awaiting Responses**: Since `aiohttp` is asynchronous, we will use `await` to handle responses.

However, since the provided code does not include any HTTP request logic, the migration will focus on preparing the structure for future asynchronous requests using `aiohttp`.

### Modified Code
```python
from typing import Any
import aiohttp
from requests.structures import CaseInsensitiveDict


class ApiException(Exception):
    def __init__(self, data: Any = None, headers: CaseInsensitiveDict = None, status_code: int = None, *args, **kwargs):
        self.data = data or kwargs
        self.headers = headers
        self.status_code = status_code


class ConfigurationException(Exception):
    pass
```

Note: The provided code does not contain any HTTP request logic, so the migration to `aiohttp` is not fully represented here. The actual usage of `aiohttp` would typically occur in a function that performs HTTP requests, which is not included in the original code snippet.