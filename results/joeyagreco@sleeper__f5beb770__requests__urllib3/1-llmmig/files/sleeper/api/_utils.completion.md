### Explanation of Changes:
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`, so the `requests` import was removed, and `urllib3` was imported instead.
2. **Creating an HTTP Connection Pool**: Unlike `requests`, `urllib3` requires an explicit `PoolManager` to manage HTTP connections. A `PoolManager` instance was created and reused for all HTTP requests.
3. **Replacing `requests.get`**: The `requests.get` calls were replaced with `urllib3.PoolManager.request` calls. The `method` parameter was set to `"GET"`, and the `url` parameter was passed as required.
4. **Handling Responses**: 
   - `urllib3` responses are not automatically parsed as JSON. The `.data` attribute of the response was decoded and passed to `json.loads` for JSON parsing.
   - The `.raise_for_status()` method from `requests` was replaced with manual status code checks, raising an exception for non-2xx status codes.
5. **Returning Content**: For the `get_content` function, the `.data` attribute of the response was used to return raw bytes.

### Modified Code:
```python
from typing import Any
import urllib3
import json

# Create a PoolManager instance for managing HTTP connections
http = urllib3.PoolManager()


def build_route(base_url: str, *paths: str | int) -> str:
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    paths = tuple(str(p).strip("/") for p in paths)
    url = f"{base_url}/{'/'.join(paths)}"
    return url.strip("/")


def add_filters(url: str, *args: tuple[str, Any]) -> str:
    """
    Adds filters to the given url.
    """
    symbol = "?"
    if "?" in url:
        symbol = "&"
    for arg in args:
        url = f"{url}{symbol}{arg[0]}={arg[1]}"
        symbol = "&"
    return url


def get(url: str) -> Any:
    response = http.request("GET", url)
    if response.status < 200 or response.status >= 300:
        raise urllib3.exceptions.HTTPError(f"HTTP request failed with status code {response.status}")
    return json.loads(response.data.decode("utf-8"))


def get_content(url: str) -> bytes:
    response = http.request("GET", url)
    if response.status < 200 or response.status >= 300:
        raise urllib3.exceptions.HTTPError(f"HTTP request failed with status code {response.status}")
    return response.data
```

### Key Notes:
- The `http` object (an instance of `urllib3.PoolManager`) is reused across all requests to optimize connection management.
- The `urllib3.exceptions.HTTPError` is raised manually for non-2xx status codes, mimicking the behavior of `requests.raise_for_status()`.
- JSON parsing is done explicitly using `json.loads`, as `urllib3` does not provide automatic JSON handling like `requests`.
- The `.data` attribute of the `urllib3` response is used to access the raw response content.