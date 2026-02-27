### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` with `pycurl` for HTTP requests**:
   - `pycurl` requires setting up a `pycurl.Curl` object and configuring it with options like the URL, timeout, and file writing.
   - The `pycurl` library does not have a direct equivalent of `requests.get` with `stream=True`. Instead, data is written directly to a file or a buffer using a callback function.
2. **Error Handling**:
   - `pycurl` raises exceptions for network errors, which are caught using `pycurl.error`.
   - HTTP status codes are checked manually using the `C.getinfo(pycurl.RESPONSE_CODE)` method.
3. **File Writing**:
   - Instead of `response.iter_content`, data is written to the file using a callback function (`C.setopt(pycurl.WRITEFUNCTION, ...)`).
4. **Headers**:
   - The `Content-Length` header is retrieved using `C.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)`.

Below is the modified code:

---

### Modified Code:
```python
"""File Downloader for snapchat_dl."""
import os
import time

import pycurl
from loguru import logger


def download_url(url: str, dest: str, sleep_interval: int):
    """Download URL to destination path.

    Args:
        url (str): url to download
        dest (str): absolute path to destination

    Raises:
        pycurl.error: if there is a network error
        FileExistsError: if file is already downloaded
    """
    if len(os.path.dirname(dest)) > 0:
        os.makedirs(os.path.dirname(dest), exist_ok=True)

    """Rate limiting."""
    time.sleep(sleep_interval)

    # Prepare to download the file
    try:
        with open(dest, "wb") as handle:
            C = pycurl.Curl()
            C.setopt(pycurl.URL, url)
            C.setopt(pycurl.TIMEOUT, 10)
            C.setopt(pycurl.FOLLOWLOCATION, True)
            C.setopt(pycurl.WRITEDATA, handle)

            try:
                C.perform()
            except pycurl.error as e:
                logger.error(f"Network error: {e}")
                raise
            finally:
                C.close()

            # Check HTTP status code
            http_status = C.getinfo(pycurl.RESPONSE_CODE)
            if http_status != 200:
                raise Exception(f"HTTP error: {http_status}")

            # Check content length
            content_length = C.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)
            if os.path.isfile(dest) and os.path.getsize(dest) == content_length:
                raise FileExistsError

            if os.path.isfile(dest) and os.path.getsize(dest) == 0:
                os.remove(dest)

    except FileExistsError as e:
        pass
```

---

### Key Notes:
1. **File Writing**:
   - The `pycurl.WRITEDATA` option is used to write the response directly to the file.
2. **Error Handling**:
   - `pycurl.error` is used to catch network-related errors.
   - HTTP status codes are checked manually after the request is performed.
3. **Content-Length**:
   - The `pycurl.CONTENT_LENGTH_DOWNLOAD` option retrieves the `Content-Length` header for comparison with the file size.

This code maintains the original functionality while replacing `requests` with `pycurl`.