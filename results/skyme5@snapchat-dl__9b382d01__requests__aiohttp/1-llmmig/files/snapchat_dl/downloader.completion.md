### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so the function `download_url` was converted to an `async` function.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` to make HTTP requests. This replaces the `requests.get` calls.
3. **Streaming Data**: The `aiohttp` equivalent of `requests.get(..., stream=True)` is to use `session.get` and read the response body in chunks using `response.content.iter_chunked`.
4. **Timeout Handling**: `aiohttp` uses `aiohttp.ClientTimeout` for timeouts, which was added to the session.
5. **Error Handling**: `aiohttp` raises exceptions like `aiohttp.ClientError` instead of `requests.exceptions.RequestException`. These were updated accordingly.
6. **File Writing**: The file writing logic remains the same, but it was adapted to work within the asynchronous context.

### Modified Code
Here is the complete code after migrating to `aiohttp`:

```python
"""File Downloader for snapchat_dl."""
import os
import time
import asyncio

import aiohttp
from loguru import logger


async def download_url(url: str, dest: str, sleep_interval: int):
    """Download URL to destination path.

    Args:
        url (str): url to download
        dest (str): absolute path to destination

    Raises:
        response.raise_for_status: if response is 4** or 50*
        FileExistsError: if file is already downloaded
    """
    if len(os.path.dirname(dest)) > 0:
        os.makedirs(os.path.dirname(dest), exist_ok=True)

    """Rate limiting."""
    await asyncio.sleep(sleep_interval)

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        status=response.status, message="Request failed"
                    )

                content_length = response.headers.get("Content-Length")
                if os.path.isfile(dest) and os.path.getsize(dest) == int(content_length):
                    raise FileExistsError

                if os.path.isfile(dest) and os.path.getsize(dest) == 0:
                    os.remove(dest)

                try:
                    with open(dest, "xb") as handle:
                        try:
                            async for data in response.content.iter_chunked(4194304):
                                handle.write(data)
                            handle.close()
                        except aiohttp.ClientError as e:
                            logger.error(e)
                except FileExistsError as e:
                    pass
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
```

### Key Notes
- The function `download_url` is now asynchronous (`async def`), so it must be called using `await` in an asynchronous context.
- The `aiohttp.ClientSession` is used to manage HTTP requests, and the `response.content.iter_chunked` method is used to stream data in chunks.
- Error handling was updated to use `aiohttp` exceptions.
- The rest of the logic, including file handling and rate limiting, remains unchanged.