### Explanation of Changes

To migrate the code from using `urllib3` to `aiohttp`, several key changes were made:

1. **Importing aiohttp**: The `aiohttp` library is imported instead of `urllib3`.
2. **Creating a ClientSession**: Instead of using a `PoolManager`, we create an `aiohttp.ClientSession` to manage connections.
3. **Making Asynchronous Requests**: The `request` function is modified to be asynchronous, using `async def` and `await` to handle the request and response.
4. **Handling SSL Certificates**: The SSL certificate handling is adjusted to use `aiohttp`'s built-in capabilities.
5. **Response Handling**: The response is now an `aiohttp.ClientResponse` object, which is handled differently than the `urllib3` response.

Here is the modified code:

```python
# =============================================================================
# Casanova HTTP Helpers
# =============================================================================
#
# HTTP Helpers working with optional aiohttp & certifi deps.
#
try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import certifi
except ImportError:
    certifi = None

from casanova.exceptions import NoHTTPSupportError

aiohttp_installed = aiohttp is not None
certifi_installed = certifi is not None

session = None

if aiohttp_installed:
    connector_kwargs = {}

    if not certifi_installed:
        connector_kwargs["ssl"] = False
    else:
        connector_kwargs["ssl"] = aiohttp.ClientSession().ssl.create_default_context(cafile=certifi.where())

    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(**connector_kwargs))


async def request(url):
    if session is None:
        raise NoHTTPSupportError(
            "casanova is not able to make http calls. please install aiohttp (and certifi if you want secure HTTPS)"
        )

    async with session.get(url) as response:
        return response
``` 

### Note
- The `request` function is now asynchronous, so it should be called within an `async` context. Make sure to adjust the calling code accordingly to handle the asynchronous nature of `aiohttp`.