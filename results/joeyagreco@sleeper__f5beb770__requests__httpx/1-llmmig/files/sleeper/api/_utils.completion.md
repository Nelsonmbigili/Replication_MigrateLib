### Explanation of Changes:
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Statement**: Replaced the `requests` import with `httpx`.
2. **GET Requests**: Updated the `requests.get` calls to `httpx.get`. The method signatures for `httpx.get` are compatible with `requests.get`, so no additional changes were needed.
3. **Response Handling**: The `httpx` response object has the same methods (`raise_for_status`, `json`, and `content`) as the `requests` response object, so no changes were required in how the response is processed.

### Modified Code:
```python
from typing import Any

import httpx


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
    response = httpx.get(url)
    response.raise_for_status()
    return response.json()


def get_content(url: str) -> bytes:
    response = httpx.get(url)
    response.raise_for_status()
    return response.content
```

### Summary:
The migration involved replacing `requests` with `httpx` and ensuring that the `httpx` methods (`get`, `raise_for_status`, `json`, and `content`) were used in place of their `requests` counterparts. No other changes were made to the code.