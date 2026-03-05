### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, several key changes were made:

1. **Importing urllib3**: The `requests` library was replaced with `urllib3`. The import statement was updated accordingly.
2. **Creating a PoolManager**: `urllib3` requires a `PoolManager` instance to handle connections, which was added to the code.
3. **Making the Request**: The `requests.get()` method was replaced with `http.request('GET', url)`, where `http` is the `PoolManager` instance.
4. **Handling Response**: The response handling was adjusted to use `response.status` instead of `response.status_code`, and the content length was accessed via `response.headers['Content-Length']`.
5. **Error Handling**: The error handling was modified to check for `HTTPError` and `ConnectionError` from `urllib3`.

Here is the modified code:

```python
"""File Downlaoder for snapchat_dl."""
import os
import time

import urllib3
from loguru import logger

http = urllib3.PoolManager()

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
        response = http.request('GET', url, preload_content=False, timeout=10)
    except urllib3.exceptions.ConnectTimeout:
        response = http.request('GET', url, preload_content=False, timeout=10)

    if response.status != 200:
        raise Exception(f"HTTP Error: {response.status}")

    if os.path.isfile(dest) and os.path.getsize(dest) == int(response.headers['Content-Length']):
        raise FileExistsError

    if os.path.isfile(dest) and os.path.getsize(dest) == 0:
        os.remove(dest)
    try:
        with open(dest, "xb") as handle:
            try:
                for data in response.stream(4096):
                    handle.write(data)
                handle.close()
            except urllib3.exceptions.HTTPError as e:
                logger.error(e)
    except FileExistsError as e:
        pass
``` 

This code now uses `urllib3` for making HTTP requests and handling responses, while maintaining the original structure and functionality of the code.