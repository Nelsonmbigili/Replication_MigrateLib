### Explanation of Changes
To migrate the code from the `requests` library to the `treq` library, the following changes were made:
1. **Asynchronous Nature of `treq`**: `treq` is built on top of `Twisted` and is asynchronous. Therefore, the function `download_url` was converted to an `async` function, and `await` was used for asynchronous calls.
2. **Replaced `requests.get` with `treq.get`**: The `requests.get` method was replaced with `treq.get`, which is asynchronous and returns a `Deferred` object. This was awaited to get the response.
3. **Replaced `response.iter_content` with `treq.content` and `treq.collect`**: `treq` does not have an `iter_content` method. Instead, the response content can be streamed using `treq.collect` or read fully using `treq.content`. In this case, `treq.collect` was used to handle chunked downloads.
4. **Error Handling**: `treq` raises exceptions differently. The `treq.get` call was wrapped in a `try-except` block to handle connection errors.
5. **Headers and Status Code**: Accessing headers and status codes in `treq` is slightly different. The `response.code` was used for the status code, and `response.headers.getRawHeaders` was used for headers.
6. **File Writing**: The file writing logic remains the same, but it was adjusted to work with the asynchronous nature of `treq`.

### Modified Code
Here is the complete code after migration to `treq`:

```python
"""File Downloader for snapchat_dl."""
import os
import time
import asyncio

import treq
from loguru import logger


async def download_url(url: str, dest: str, sleep_interval: int):
    """Download URL to destination path.

    Args:
        url (str): url to download
        dest (str): absolute path to destination

    Raises:
        Exception: if response is 4** or 50*
        FileExistsError: if file is already downloaded
    """
    if len(os.path.dirname(dest)) > 0:
        os.makedirs(os.path.dirname(dest), exist_ok=True)

    """Rate limiting."""
    time.sleep(sleep_interval)

    try:
        response = await treq.get(url, timeout=10)
    except Exception as e:
        logger.error(f"Connection error: {e}")
        response = await treq.get(url, timeout=10)

    if response.code != 200:  # Equivalent to requests.codes.ok
        raise Exception(f"HTTP Error: {response.code}")

    content_length = response.headers.getRawHeaders("content-length")
    content_length = int(content_length[0]) if content_length else None

    if os.path.isfile(dest) and os.path.getsize(dest) == content_length:
        raise FileExistsError

    if os.path.isfile(dest) and os.path.getsize(dest) == 0:
        os.remove(dest)

    try:
        with open(dest, "xb") as handle:
            try:
                async def write_chunk(chunk):
                    handle.write(chunk)

                await treq.collect(response, write_chunk)
                handle.close()
            except Exception as e:
                logger.error(e)
    except FileExistsError as e:
        pass
```

### Key Notes:
- The function `download_url` is now asynchronous (`async def`), so it must be called using `await` or run in an event loop.
- The `treq.collect` method is used to handle streaming the response content in chunks.
- The `response.headers.getRawHeaders` method retrieves headers as a list, so additional processing is required to extract the value.
- The `time.sleep` call remains synchronous, as it is unrelated to the `treq` library. If desired, it could be replaced with `await asyncio.sleep` for full asynchronous behavior.