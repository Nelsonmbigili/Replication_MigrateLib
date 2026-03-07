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
