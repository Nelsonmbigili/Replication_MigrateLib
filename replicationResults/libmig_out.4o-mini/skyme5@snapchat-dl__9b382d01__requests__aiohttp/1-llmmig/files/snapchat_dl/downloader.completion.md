### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, several key changes were made:

1. **Asynchronous Functionality**: The `download_url` function was modified to be asynchronous. This requires the use of `async def` and the `await` keyword for asynchronous calls.
2. **Session Management**: Instead of directly calling `requests.get`, we create an `aiohttp.ClientSession` to manage connections and make requests.
3. **Error Handling**: The error handling for timeouts and status codes was adapted to work with `aiohttp` exceptions and response objects.
4. **File Writing**: The file writing process remains largely the same, but it is now wrapped in an asynchronous context.

### Modified Code
Here is the complete modified code using `aiohttp`:

```python
"""File Downlaoder for snapchat_dl."""
import os
import time
import aiohttp
import asyncio
from loguru import logger


async def download_url(url: str, dest: str, sleep_interval: int):
    """Download URL to destionation path.

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

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        status=response.status,
                        message=response.reason
                    )

                if os.path.isfile(dest) and os.path.getsize(dest) == response.headers.get(
                    "content-length"
                ):
                    raise FileExistsError

                if os.path.isfile(dest) and os.path.getsize(dest) == 0:
                    os.remove(dest)

                with open(dest, "xb") as handle:
                    try:
                        while True:
                            data = await response.content.read(4194304)
                            if not data:
                                break
                            handle.write(data)
                    except aiohttp.ClientError as e:
                        logger.error(e)
        except FileExistsError as e:
            pass
```

### Notes
- The `asyncio.sleep` function is used instead of `time.sleep` to avoid blocking the event loop.
- The `aiohttp.ClientResponseError` is raised for non-200 status codes.
- The file writing loop reads data asynchronously from the response content.