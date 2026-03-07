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
