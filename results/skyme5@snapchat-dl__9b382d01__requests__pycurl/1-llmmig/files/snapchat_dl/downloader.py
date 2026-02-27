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
