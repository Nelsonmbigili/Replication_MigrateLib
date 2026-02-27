### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Request Method Update**: Replaced `requests.get` with `session.get` to use the `FuturesSession` instance for making requests.
4. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is called to get the actual response object before processing it.

These changes ensure that the code now uses `requests_futures` for asynchronous request handling while maintaining the original functionality.

---

### Modified Code:
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

    try:
        future = session.get(url, stream=True, timeout=10)
        response = future.result()
    except requests.exceptions.ConnectTimeout:
        future = session.get(url, stream=True, timeout=10)
        response = future.result()

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

---

### Key Notes:
- The `FuturesSession` class from `requests_futures` is used to handle asynchronous requests.
- The `.result()` method is called on the `Future` object to retrieve the actual response before processing it.
- No other changes were made to the logic or structure of the code to ensure compatibility with the rest of the application.