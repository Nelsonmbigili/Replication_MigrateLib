### Explanation of Changes
To migrate the code from `aiohttp` to `httpx`, the following changes were made:
1. **Session Initialization**: Replaced `aiohttp.ClientSession` with `httpx.AsyncClient`. The `TCPConnector` and its `verify_ssl` parameter were replaced with `httpx`'s `verify` parameter.
2. **Request Method**: Replaced `session.request` with `httpx.AsyncClient.request`. The parameters and behavior remain the same.
3. **Session Lifecycle**: `httpx.AsyncClient` does not require an explicit event loop during initialization, so the `loop` parameter was removed.
4. **Response Object**: The `httpx.Response` object is returned instead of `aiohttp.ClientResponse`. The calling code should handle this change if it relies on specific `aiohttp` response methods.

### Modified Code
```python
"""

    migro.uploader.utils
    ~~~~~~~~~~~~~~~~~~~~

    Helpers functions.

"""
import hashlib
import hmac
import time
from urllib.parse import urljoin

import httpx

from migro import __version__ as version
from migro import settings

session = httpx.AsyncClient(verify=False)


async def request(path, params=None):
    """Makes GET upload API request with specific path and params.

    :param path: Request path.
    :param params: Request params.

    :return: httpx.Response.

    """
    path = path.lstrip('/')
    url = urljoin(settings.UPLOAD_BASE, path)

    headers = {
        "User-Agent": f"Migro/{version}/{settings.PUBLIC_KEY}"
    }

    if params is None:
        params = {}
    params['pub_key'] = settings.PUBLIC_KEY
    params['UPLOADCARE_PUB_KEY'] = settings.PUBLIC_KEY

    if settings.SECRET_KEY:
        expire_timestamp = generate_expire_timestamp()
        upload_signature = generate_secure_signature(settings.SECRET_KEY, expire_timestamp)

        params['signature'] = upload_signature
        params['expire'] = expire_timestamp

    response = await session.request(
        method='GET',
        url=url,
        headers=headers,
        params=params,
        follow_redirects=True)
    return response


def generate_expire_timestamp(minutes_ahead=5):
    """Generate expiration timestamp for specified minutes after current time.

    :param minutes_ahead: Minutes after current time.

    :return: int.

    """
    expire_timestamp = int(time.time()) + 60 * minutes_ahead

    return expire_timestamp


def generate_secure_signature(secret, expire):
    """Generate secure signature with specified secret and expiration timestamp.

    :param secret: Secret Key.
    :param expire: Expiration timestamp.

    :return: str.

    """
    k, m = secret, str(expire).encode('utf-8')
    if not isinstance(k, (bytes, bytearray)):
        k = k.encode('utf-8')

    return hmac.new(k, m, hashlib.sha256).hexdigest()
```

### Key Notes
- The `httpx.AsyncClient` is used as a direct replacement for `aiohttp.ClientSession`.
- The `verify_ssl=False` in `aiohttp.TCPConnector` was replaced with `verify=False` in `httpx.AsyncClient`.
- The `follow_redirects=True` parameter in `httpx` replaces `allow_redirects=True` in `aiohttp`.
- The return type of the `request` function is now `httpx.Response`. Ensure that any downstream code interacting with the response object is compatible with `httpx`.