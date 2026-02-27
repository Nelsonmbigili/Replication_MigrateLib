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
