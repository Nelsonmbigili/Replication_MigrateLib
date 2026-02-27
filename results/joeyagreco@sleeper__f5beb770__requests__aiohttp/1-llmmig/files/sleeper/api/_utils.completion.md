### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Nature**: `aiohttp` is an asynchronous library, so the `get` and `get_content` functions were modified to be `async` functions.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` to make requests. A session is created within the `get` and `get_content` functions using an `async with` block.
3. **Response Handling**: The `aiohttp` response object provides methods like `.json()` and `.read()` for accessing the response body. These methods are asynchronous, so they are awaited.
4. **Error Handling**: `aiohttp` raises exceptions for HTTP errors, similar to `requests`. The `raise_for_status()` method is used to ensure HTTP errors are raised.

Below is the modified code.

---

### Modified Code
```python
from typing import Any

import aiohttp


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


async def get(url: str) -> Any:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()


async def get_content(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.read()
```

---

### Key Notes
1. **Asynchronous Usage**: Since `aiohttp` is asynchronous, the `get` and `get_content` functions must be called using `await` in an asynchronous context.
2. **Session Management**: The `async with aiohttp.ClientSession()` ensures proper cleanup of resources after the request is completed.
3. **Compatibility**: The function signatures and return types remain unchanged, ensuring compatibility with the rest of the application.