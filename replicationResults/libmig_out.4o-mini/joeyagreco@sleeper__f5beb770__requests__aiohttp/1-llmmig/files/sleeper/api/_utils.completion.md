### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Importing aiohttp**: The `requests` library was replaced with `aiohttp`, which is designed for asynchronous HTTP requests.
2. **Asynchronous Functions**: The `get` and `get_content` functions were modified to be asynchronous. This requires the use of the `async` keyword and the `await` keyword when making requests.
3. **Session Management**: In `aiohttp`, it's common to use a session for making requests. Therefore, a session context manager (`async with aiohttp.ClientSession() as session`) was added to handle the requests.
4. **Response Handling**: The way to handle the response and extract JSON or content changed slightly to accommodate the asynchronous nature of `aiohttp`.

Here is the modified code:

```python
from typing import Any
import aiohttp
import asyncio


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

### Note
- The `get` and `get_content` functions are now asynchronous and should be called within an asynchronous context (e.g., using `asyncio.run()` or within another async function).
- Ensure that the rest of your application is set up to handle asynchronous calls appropriately.