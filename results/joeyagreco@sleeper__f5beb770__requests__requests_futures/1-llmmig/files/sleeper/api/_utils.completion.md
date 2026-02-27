### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Method Changes**: Updated the `get` and `get_content` functions to use the `session.get` method from `FuturesSession`. Since `requests_futures` returns a `Future` object, the `.result()` method is called to retrieve the response synchronously (to maintain the original behavior).
4. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the larger application.

### Modified Code:
```python
from typing import Any

from requests_futures.sessions import FuturesSession

# Initialize a FuturesSession for asynchronous requests
session = FuturesSession()


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
    response = session.get(url).result()  # Use .result() to get the response synchronously
    response.raise_for_status()
    return response.json()


def get_content(url: str) -> bytes:
    response = session.get(url).result()  # Use .result() to get the response synchronously
    response.raise_for_status()
    return response.content
```

### Key Notes:
- The `FuturesSession` class from `requests_futures` is used to handle asynchronous requests. However, since the original code is synchronous, the `.result()` method is called to block until the request is complete.
- The `session` object is initialized globally to mimic the behavior of the original `requests` library.
- No other parts of the code were modified to ensure compatibility with the larger application.