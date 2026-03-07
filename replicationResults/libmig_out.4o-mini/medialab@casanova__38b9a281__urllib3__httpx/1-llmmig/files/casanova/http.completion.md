### Explanation of Changes

To migrate the code from using `urllib3` to `httpx`, the following changes were made:

1. **Importing httpx**: The import statement for `urllib3` was replaced with `httpx`.
2. **Creating a Client**: Instead of using `urllib3.PoolManager`, we create an `httpx.Client` instance. This client handles connection pooling and other configurations.
3. **Handling Certificates**: The certificate handling logic was adapted to `httpx`. The `verify` parameter is used to specify whether to verify SSL certificates, and it can be set to `certifi.where()` if `certifi` is installed.
4. **Making Requests**: The request method was changed from `pool_manager.request` to `client.get`, which is the method used in `httpx` to perform GET requests.
5. **Response Handling**: The response object from `httpx` does not require the `_fp.isclosed` workaround, as it handles response closure differently.

### Modified Code

```python
# =============================================================================
# Casanova HTTP Helpers
# =============================================================================
#
# HTTP Helpers working with optional httpx & certifi deps.
#
try:
    import httpx
except ImportError:
    httpx = None

try:
    import certifi
except ImportError:
    certifi = None

from casanova.exceptions import NoHTTPSupportError

httpx_installed = httpx is not None
certifi_installed = certifi is not None

client = None

if httpx_installed:
    client_kwargs = {}

    if not certifi_installed:
        client_kwargs["verify"] = False
    else:
        client_kwargs["verify"] = certifi.where()

    client = httpx.Client(**client_kwargs)


def request(url):
    if client is None:
        raise NoHTTPSupportError(
            "casanova is not able to make http calls. please install httpx (and certifi if you want secure HTTPS)"
        )

    response = client.get(url)

    return response
```