### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Import Replacement**: Replaced the `requests` import with `urllib3`.
2. **HTTP Request**: Replaced `requests.get` with `urllib3.PoolManager().request` for making HTTP requests.
3. **Timeout Handling**: Used `urllib3`'s `timeout` parameter in the `request` method.
4. **Stream Handling**: Replaced `response.iter_content` with a loop over `response.read(chunk_size)` to handle streamed content.
5. **Status Code Check**: Replaced `response.status_code` and `requests.codes.get("ok")` with `response.status` and `200` respectively.
6. **Headers Access**: Accessed headers using `response.headers` (already a dictionary in `urllib3`).
7. **Exception Handling**: Replaced `requests.exceptions.RequestException` and `requests.exceptions.ConnectTimeout` with `urllib3.exceptions.RequestError` and `urllib3.exceptions.ConnectTimeoutError`.

### Modified Code
Here is the complete code after migration to `urllib3`:

```python
"""File Downlaoder for snapchat_dl."""
import os
import time

import urllib3
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

    http = urllib3.PoolManager()

    try:
        response = http.request("GET", url, preload_content=False, timeout=10)
    except urllib3.exceptions.ConnectTimeoutError:
        response = http.request("GET", url, preload_content=False, timeout=10)

    if response.status != 200:
        raise Exception(f"HTTP Error: {response.status}")

    if os.path.isfile(dest) and os.path.getsize(dest) == int(
        response.headers.get("Content-Length", 0)
    ):
        raise FileExistsError

    if os.path.isfile(dest) and os.path.getsize(dest) == 0:
        os.remove(dest)
    try:
        with open(dest, "xb") as handle:
            try:
                chunk_size = 4194304
                while True:
                    data = response.read(chunk_size)
                    if not data:
                        break
                    handle.write(data)
                handle.close()
            except urllib3.exceptions.RequestError as e:
                logger.error(e)
    except FileExistsError as e:
        pass
    finally:
        response.release_conn()
```

### Key Notes
- The `urllib3.PoolManager` is used to manage HTTP connections.
- The `preload_content=False` parameter ensures that the response content is not automatically read into memory, allowing for streaming.
- The `response.read(chunk_size)` method is used to read the response in chunks, similar to `response.iter_content` in `requests`.
- The `response.release_conn()` method is called in the `finally` block to ensure the connection is properly released after use.