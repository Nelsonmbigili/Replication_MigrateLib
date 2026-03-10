### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `from requests_futures.sessions import FuturesSession`. This allows us to use the `FuturesSession` class, which supports asynchronous requests.
  
2. **Session Initialization**: A `FuturesSession` object was created to handle the requests asynchronously.

3. **Making Asynchronous Requests**: The `get` and `get_content` functions were modified to use the `session.get()` method from `FuturesSession`, which returns a `Future` object. We then called `result()` on the `Future` to get the actual response.

4. **Error Handling**: The error handling remains the same, as we still call `raise_for_status()` on the response object.

Here is the modified code:

```python
from typing import Any
from requests_futures.sessions import FuturesSession


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
    session = FuturesSession()
    future = session.get(url)
    response = future.result()
    response.raise_for_status()
    return response.json()


def get_content(url: str) -> bytes:
    session = FuturesSession()
    future = session.get(url)
    response = future.result()
    response.raise_for_status()
    return response.content
```