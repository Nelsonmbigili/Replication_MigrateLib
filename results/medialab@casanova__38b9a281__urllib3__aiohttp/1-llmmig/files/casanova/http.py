# =============================================================================
# Casanova HTTP Helpers
# =============================================================================
#
# HTTP Helpers working with optional aiohttp deps.
#
try:
    import aiohttp
except ImportError:
    aiohttp = None

from casanova.exceptions import NoHTTPSupportError

aiohttp_installed = aiohttp is not None

session = None

if aiohttp_installed:
    session = aiohttp.ClientSession()

async def request(url):
    if session is None:
        raise NoHTTPSupportError(
            "casanova is not able to make http calls. please install aiohttp"
        )

    async with session.get(url) as response:
        # aiohttp automatically handles SSL verification
        return response
