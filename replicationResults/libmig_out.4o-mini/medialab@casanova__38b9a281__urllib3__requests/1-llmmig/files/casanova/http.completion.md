### Explanation of Changes
To migrate the code from using the `urllib3` library to the `requests` library, the following changes were made:

1. **Importing Requests**: The `requests` library is imported instead of `urllib3`.
2. **Removing Pool Manager**: The concept of a pool manager is not needed with `requests`, as it handles connections internally.
3. **Request Method**: The `request` method is simplified to use `requests.get()` instead of `pool_manager.request()`.
4. **Response Handling**: The response object from `requests` does not require the `_fp.isclosed` workaround, as it manages the connection state differently.

### Modified Code
```python
# =============================================================================
# Casanova HTTP Helpers
# =============================================================================
#
# HTTP Helpers working with optional requests & certifi deps.
#
try:
    import requests
except ImportError:
    requests = None

try:
    import certifi
except ImportError:
    certifi = None

from casanova.exceptions import NoHTTPSupportError

requests_installed = requests is not None
certifi_installed = certifi is not None

def request(url):
    if not requests_installed:
        raise NoHTTPSupportError(
            "casanova is not able to make http calls. please install requests (and certifi if you want secure HTTPS)"
        )

    if certifi_installed:
        response = requests.get(url, verify=certifi.where())
    else:
        response = requests.get(url, verify=False)

    return response
```