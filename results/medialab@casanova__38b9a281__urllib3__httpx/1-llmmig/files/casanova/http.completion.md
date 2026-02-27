### Explanation of Changes
To migrate the code from `urllib3` to `httpx`, the following changes were made:
1. Replaced the `urllib3.PoolManager` with `httpx.Client`, which serves a similar purpose for managing HTTP connections.
2. Removed the conditional logic for `certifi` and `urllib3` imports, as `httpx` natively handles SSL certificates and does not require `certifi` to be explicitly managed.
3. Updated the `request` function to use `httpx.Client` for making HTTP requests. The `httpx` library automatically handles SSL verification, so there is no need to manually configure certificate requirements.
4. Removed the workaround for `response._fp.isclosed`, as `httpx` does not require this adjustment.

Below is the modified code using `httpx`.

---

### Modified Code
```python
# =============================================================================
# Casanova HTTP Helpers
# =============================================================================
#
# HTTP Helpers working with optional httpx deps.
#
try:
    import httpx
except ImportError:
    httpx = None

from casanova.exceptions import NoHTTPSupportError

httpx_installed = httpx is not None

client = None

if httpx_installed:
    client = httpx.Client()

def request(url):
    if client is None:
        raise NoHTTPSupportError(
            "casanova is not able to make http calls. please install httpx"
        )

    response = client.get(url)

    return response
```

---

### Key Notes
- The `httpx.Client` is used to manage HTTP connections, similar to `urllib3.PoolManager`.
- The `httpx` library automatically handles SSL certificate verification, so there is no need for manual configuration with `certifi`.
- The `request` function now uses `client.get(url)` to perform the HTTP GET request.
- The `response._fp.isclosed` workaround is no longer necessary, as `httpx` does not have this issue.