### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Function Calls**: Updated the `requests.get()` calls to `httpx.get()`. The usage remains the same, as both libraries have similar interfaces for making GET requests.
3. **Response Handling**: The response handling remains unchanged since both libraries provide similar methods for checking the status and accessing JSON and content.

### Modified Code
Here is the modified code after migrating to `httpx`:

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