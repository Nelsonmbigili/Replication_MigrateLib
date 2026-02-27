The following Python code currently uses the library "aiohttp" version 3.9.5.
Migrate this code to use the library "httpx" version 0.28.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "aiohttp" to "httpx".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "aiohttp" and "httpx".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
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

from aiohttp import ClientSession, TCPConnector

from migro import __version__ as version
from migro import settings

loop = get_event_loop()
session = ClientSession(connector=TCPConnector(verify_ssl=False, loop=loop))


async def request(path, params=None):
    """Makes GET upload API request with specific path and params.

    :param path: Request path.
    :param params: Request params.

    :return: aiohttp.ClientResponse.

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
        method='get',
        url=url,
        headers=headers,
        allow_redirects=True,
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