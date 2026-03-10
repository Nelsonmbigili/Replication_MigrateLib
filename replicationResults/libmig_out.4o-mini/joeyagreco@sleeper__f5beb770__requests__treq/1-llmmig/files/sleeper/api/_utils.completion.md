### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `treq`.
2. **Function Calls**: The `requests.get()` calls were replaced with `treq.get()`. The `treq` library has a similar API to `requests`, so the method calls remain largely the same.
3. **Response Handling**: The way to access the response content and JSON data is similar in `treq`, so the calls to `response.json()` and `response.content` were retained without modification.

Here is the modified code:

```python
from typing import Any

import treq


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
    response = treq.get(url)
    response.raise_for_status()
    return response.json()


def get_content(url: str) -> bytes:
    response = treq.get(url)
    response.raise_for_status()
    return response.content
```