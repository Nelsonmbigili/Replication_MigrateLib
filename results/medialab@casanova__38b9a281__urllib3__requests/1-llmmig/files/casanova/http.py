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
