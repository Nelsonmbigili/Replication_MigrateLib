### Explanation of Changes:
To migrate the code from using `urllib3` to `requests`, the following changes were made:
1. Removed all references to `urllib3` and `certifi`, as `requests` handles HTTPS and certificate verification internally.
2. Replaced the `urllib3.PoolManager` with the `requests` library's `requests.get` function for making HTTP GET requests.
3. Removed the `pool_manager` initialization logic, as `requests` does not require a separate pool manager.
4. Updated the `request` function to use `requests.get` instead of `pool_manager.request`.
5. Removed the workaround for `response._fp.isclosed`, as it is not needed with `requests`.

### Modified Code:
```python
# =============================================================================
# Casanova HTTP Helpers
# =============================================================================
#
# HTTP Helpers working with optional requests deps.
#
try:
    import requests
except ImportError:
    requests = None

from casanova.exceptions import NoHTTPSupportError

requests_installed = requests is not None


def request(url):
    if not requests_installed:
        raise NoHTTPSupportError(
            "casanova is not able to make http calls. please install the 'requests' library."
        )

    response = requests.get(url, stream=True)

    return response
```