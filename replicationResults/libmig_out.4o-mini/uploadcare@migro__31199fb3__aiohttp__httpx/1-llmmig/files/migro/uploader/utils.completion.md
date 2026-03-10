### Explanation of Changes

To migrate the code from using the `aiohttp` library to the `httpx` library, the following changes were made:

1. **Import Statement**: The import for `ClientSession` and `TCPConnector` from `aiohttp` was replaced with `httpx`.
2. **Session Creation**: The `ClientSession` from `aiohttp` was replaced with `httpx.Client()`. The `httpx` library does not require a separate connector for SSL verification, so the `verify_ssl` parameter was removed.
3. **Request Method**: The `session.request` method from `aiohttp` was replaced with `session.get` from `httpx`, as we are only making GET requests in this code.
4. **Response Handling**: The return type of the request is now an `httpx.Response` object instead of `aiohttp.ClientResponse`.

Here is the modified code:

```python
"""

    migro.uploader.utils
    ~~~~~~~~~~~~~~~~~~~~

    Helpers functions.

"""
import hashlib
import hmac
import time
from asyncio import get_event_loop
from urllib.parse import urljoin

import httpx

from migro import __version__ as version
from migro import settings

loop = get_event_loop()
session = httpx.Client()

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

    response = await session.get(
        url=url,
        headers=headers,
        params=params)
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