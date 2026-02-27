### Explanation of Changes:
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Import Changes**: Replaced the `requests` import with `treq`.
2. **Asynchronous Nature of `treq`**: The `treq` library is asynchronous, so the `get` and `get_content` functions were modified to be `async` functions. This means they now return `awaitable` results.
3. **HTTP Requests**: Replaced `requests.get` with `treq.get`. The `treq.get` method returns a `Response` object, which requires additional steps to extract JSON or content.
4. **Response Handling**:
   - For JSON responses, used `response.json()` (awaited).
   - For content responses, used `response.content()` (awaited).
5. **Error Handling**: The `treq` library does not have a `raise_for_status` method. Instead, the status code is checked manually, and an exception is raised if the status code indicates an error.

### Modified Code:
```python
from typing import Any
import treq
from twisted.internet.defer import ensureDeferred


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
    response = await treq.get(url)
    if response.code >= 400:
        raise Exception(f"HTTP Error: {response.code}")
    return await response.json()


async def get_content(url: str) -> bytes:
    response = await treq.get(url)
    if response.code >= 400:
        raise Exception(f"HTTP Error: {response.code}")
    return await response.content()
```

### Key Notes:
- The `get` and `get_content` functions are now `async` functions, so they must be called with `await` in an asynchronous context.
- If the application is not already asynchronous, you may need to use `ensureDeferred` or refactor the calling code to support asynchronous execution.
- The `treq` library uses Twisted under the hood, so the application must have Twisted installed and properly configured.