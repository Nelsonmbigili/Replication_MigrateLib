### Explanation of Changes
To migrate the code from `urllib3` to `aiohttp`, the following changes were made:
1. **Library Import**: Replaced `urllib3` and `certifi` imports with `aiohttp`.
2. **Session Management**: Replaced `urllib3.PoolManager` with an `aiohttp.ClientSession` for managing HTTP connections.
3. **Request Handling**: Updated the `request` function to use `aiohttp`'s asynchronous `ClientSession.get` method.
4. **Error Handling**: Removed the `certifi` dependency and replaced it with `aiohttp`'s built-in SSL handling.
5. **Asynchronous Code**: Since `aiohttp` is asynchronous, the `request` function was updated to be an `async` function, and the response handling was adjusted accordingly.

Below is the modified code:

---

### Modified Code
```python
# =============================================================================
# Casanova HTTP Helpers
# =============================================================================
#
# HTTP Helpers working with optional aiohttp deps.
#
try:
    import aiohttp
except ImportError:
    aiohttp = None

from casanova.exceptions import NoHTTPSupportError

aiohttp_installed = aiohttp is not None

session = None

if aiohttp_installed:
    session = aiohttp.ClientSession()

async def request(url):
    if session is None:
        raise NoHTTPSupportError(
            "casanova is not able to make http calls. please install aiohttp"
        )

    async with session.get(url) as response:
        # aiohttp automatically handles SSL verification
        return response
```

---

### Key Notes:
1. **Asynchronous Nature**: The `request` function is now asynchronous (`async def`), so it must be awaited when called.
2. **Session Management**: The `aiohttp.ClientSession` is created globally and reused for all requests, similar to how `urllib3.PoolManager` was used.
3. **SSL Handling**: `aiohttp` handles SSL verification internally, so there is no need for `certifi` or manual SSL configuration.
4. **Response Handling**: The `aiohttp` response object is returned directly, and the caller can handle it as needed.

This code assumes that the rest of the application is updated to handle the asynchronous nature of the `request` function.