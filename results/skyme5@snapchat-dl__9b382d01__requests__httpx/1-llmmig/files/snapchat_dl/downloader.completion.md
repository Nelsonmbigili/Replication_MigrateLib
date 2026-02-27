### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: Replaced `import requests` with `import httpx`.
2. **HTTP Client**: Replaced `requests.get` with `httpx.get`. The `httpx` library provides a similar interface for making HTTP requests.
3. **Timeout Handling**: Updated the timeout handling to use `httpx`'s `timeout` parameter, which works similarly to `requests`.
4. **Exception Handling**: Replaced `requests.exceptions.ConnectTimeout` and `requests.exceptions.RequestException` with their `httpx` equivalents: `httpx.ConnectTimeout` and `httpx.RequestError`.
5. **Status Code Check**: Updated the status code check to use `httpx.codes.OK` instead of `requests.codes.get("ok")`.
6. **Streaming Response**: The `iter_content` method in `requests` is replaced with `iter_bytes` in `httpx` for streaming response content.

### Modified Code
Here is the complete code after migrating to `httpx`:

```python
"""File Downlaoder for snapchat_dl."""
import os
import time

import httpx
from loguru import logger


def download_url(url: str, dest: str, sleep_interval: int):
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
    time.sleep(sleep_interval)

    try:
        response = httpx.get(url, stream=True, timeout=10)
    except httpx.ConnectTimeout:
        response = httpx.get(url, stream=True, timeout=10)

    if response.status_code != httpx.codes.OK:
        raise response.raise_for_status()

    if os.path.isfile(dest) and os.path.getsize(dest) == response.headers.get(
        "content-length"
    ):
        raise FileExistsError

    if os.path.isfile(dest) and os.path.getsize(dest) == 0:
        os.remove(dest)
    try:
        with open(dest, "xb") as handle:
            try:
                for data in response.iter_bytes(chunk_size=4194304):
                    handle.write(data)
                handle.close()
            except httpx.RequestError as e:
                logger.error(e)
    except FileExistsError as e:
        pass
```

### Key Notes
- The `httpx` library provides a very similar API to `requests`, so the migration required minimal changes.
- The `iter_bytes` method in `httpx` is the equivalent of `iter_content` in `requests` for streaming data.
- The exception classes in `httpx` are slightly different but serve the same purpose as those in `requests`.