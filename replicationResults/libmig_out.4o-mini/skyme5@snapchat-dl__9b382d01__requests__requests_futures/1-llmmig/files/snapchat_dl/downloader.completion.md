### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The `requests` library was replaced with `requests_futures.sessions` to utilize the `FuturesSession` class, which allows for asynchronous requests.
2. **Session Creation**: Instead of directly calling `requests.get()`, a `FuturesSession` object was created, and the `get()` method was called on this object.
3. **Handling the Response**: The response from the `FuturesSession.get()` method is now a `Future` object, so we need to call `.result()` to get the actual response object.
4. **Error Handling**: The error handling remains the same, but it now operates on the result of the future.

Here is the modified code:

```python
"""File Downlaoder for snapchat_dl."""
import os
import time

from requests_futures.sessions import FuturesSession
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

    session = FuturesSession()
    future_response = session.get(url, stream=True, timeout=10)
    
    try:
        response = future_response.result()
    except requests.exceptions.ConnectTimeout:
        response = future_response.result()

    if response.status_code != requests.codes.get("ok"):
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
                for data in response.iter_content(chunk_size=4194304):
                    handle.write(data)
                handle.close()
            except requests.exceptions.RequestException as e:
                logger.error(e)
    except FileExistsError as e:
        pass
```