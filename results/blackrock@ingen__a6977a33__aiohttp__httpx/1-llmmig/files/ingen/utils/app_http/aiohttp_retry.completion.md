### Explanation of Changes:
To migrate the code from `aiohttp` to `httpx`, the following changes were made:
1. Replaced `aiohttp.ClientSession` with `httpx.AsyncClient`.
2. Updated the `async with` block to use `httpx`'s request methods (`get`, `post`, etc.) via `AsyncClient`.
3. Adjusted the response handling:
   - `response.status` in `aiohttp` is replaced with `response.status_code` in `httpx`.
   - `response.headers` remains the same.
   - For JSON responses, `response.json()` is used (similar to `aiohttp`).
   - For text responses, `response.text` is accessed directly (no need for `await` as in `aiohttp`).
4. Updated the `session` parameter type in the function docstring to reflect the use of `httpx.AsyncClient`.

Below is the modified code:

---

### Modified Code:
```python
#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import asyncio
import logging
from collections import namedtuple

from httpx import AsyncClient

from ingen.utils.app_http.success_criterias import status_criteria, DEFAULT_STATUS_CRITERIA_OPTIONS

logger = logging.getLogger()

HTTPResponse = namedtuple('HTTPResponse', ['status', 'headers', 'data'])


async def http_retry_request(
        session: AsyncClient,
        method,
        url,
        retries=2,
        interval=1,
        interval_increment=2,
        success_criteria=status_criteria,
        criteria_options=DEFAULT_STATUS_CRITERIA_OPTIONS,
        **kwargs):
    """
    Asynchronously retries the HTTP call until the given success_criteria (a callable) is succeeded or
    number of retries reaches to zero
    :param session: httpx AsyncClient
    :param method: HTTP Methods
    :param url: Request URL
    :param retries: How many times to retry
    :param interval: How long to wait before retrying (in seconds)
    :param interval_increment: Number of seconds added to interval when retrying.
                               So if a request fails with following params:
                               retires = 4, interval = 2, interval_increment = 2
                               4 retries will be made after 2, 4, 6, and 8 seconds.
    :param success_criteria: a callable that defines the success_criteria,
                             see 'src.utils.app_http.success_criterias.py' for more
    :param criteria_options: dict-like options required by success_criteria method
    :param kwargs: additional kwargs for HTTP methods, eg., headers, auth, data etc
    :return: If successful, returns a namedtuple HTTPResponse containing response status, headers and body,
             otherwise None
    """

    _method = method.lower()
    if _method not in ["get", "post", "put", "patch", "delete"]:
        raise ValueError("Unsupported HTTP method passed for retry")

    attempt = retries + 1
    should_retry = None

    while attempt != 0:
        attempt -= 1
        wait_time = interval
        if should_retry:
            wait_time = wait_time + interval_increment
            await asyncio.sleep(wait_time)
        async with session as client:
            try:
                response = await getattr(client, _method)(url, **kwargs)
                logger.info(f"awaiting {_method.upper()} {url}")

                status = response.status_code
                headers = response.headers

                if headers.get('Content-Type') and 'application/json' in headers.get('Content-Type', ''):
                    data = response.json()
                else:
                    data = response.text
            except Exception as e:
                raise ConnectionError(f"Error occurred while getting response from url {url}: {e}")

            http_response = HTTPResponse(status, headers, data)
            logger.info(f"Response for {url}: {http_response}")

            if success_criteria(http_response, criteria_options):
                return http_response

            should_retry = True
            logger.info(f"Retrying in {wait_time} seconds")

    logger.error(f"Could not get a successful response for url: {url} after {retries} retries.")
```

---

### Key Notes:
- The migration ensures that the behavior of the function remains consistent while using `httpx` instead of `aiohttp`.
- The `httpx.AsyncClient` is used in the same way as `aiohttp.ClientSession`, maintaining the asynchronous nature of the function.
- The changes are minimal and focused solely on replacing `aiohttp` with `httpx`.