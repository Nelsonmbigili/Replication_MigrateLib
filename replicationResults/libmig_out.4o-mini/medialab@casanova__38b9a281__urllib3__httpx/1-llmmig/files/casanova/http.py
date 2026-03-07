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
