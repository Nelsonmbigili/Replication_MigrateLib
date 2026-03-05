### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Request Method**: Replaced `requests.get` with `httpx.get`.
3. **Response Handling**: Updated the way to check for successful responses. Instead of checking `response.status_code` against `requests.codes.get("ok")`, we directly check if `response.is_success`.
4. **Exception Handling**: Changed the exception handling from `requests.exceptions.ConnectTimeout` and `requests.exceptions.RequestException` to `httpx.ConnectTimeout` and `httpx.RequestError`, respectively.
5. **Response Content Iteration**: The method to iterate over the response content remains the same, but it is now using `httpx`'s response object.

Here is the modified code:

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

    if not response.is_success:
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