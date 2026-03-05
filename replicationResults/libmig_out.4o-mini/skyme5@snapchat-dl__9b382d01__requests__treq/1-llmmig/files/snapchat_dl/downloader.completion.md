### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `treq`.
2. **Request Method**: Replaced `requests.get` with `treq.get`.
3. **Response Handling**: Instead of checking `response.status_code`, we use `response.raise_for_status()` directly, as `treq` raises an exception for HTTP errors.
4. **Content Iteration**: Changed the way to read the response content. `treq` provides a `response.iter_content()` method similar to `requests`, but it is accessed differently.
5. **Exception Handling**: Adjusted the exception handling to catch `treq.exceptions.RequestException` instead of `requests.exceptions.RequestException`.

Here is the modified code:

```python
"""File Downlaoder for snapchat_dl."""
import os
import time

import treq
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
        response = treq.get(url, stream=True, timeout=10)
    except treq.exceptions.ConnectTimeout:
        response = treq.get(url, stream=True, timeout=10)

    response.raise_for_status()

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
            except treq.exceptions.RequestException as e:
                logger.error(e)
    except FileExistsError as e:
        pass
```