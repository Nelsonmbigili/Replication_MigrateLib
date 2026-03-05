"""File Downlaoder for snapchat_dl."""
import os
import time
import pycurl
from io import BytesIO
from loguru import logger


def download_url(url: str, dest: str, sleep_interval: int):
    """Download URL to destionation path.

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

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.TIMEOUT, 10)

    try:
        c.perform()
        http_code = c.getinfo(c.RESPONSE_CODE)
    except pycurl.error as e:
        logger.error(e)
        return

    c.close()

    if http_code != 200:
        raise Exception(f"HTTP error: {http_code}")

    if os.path.isfile(dest) and os.path.getsize(dest) == buffer.getbuffer().nbytes:
        raise FileExistsError

    if os.path.isfile(dest) and os.path.getsize(dest) == 0:
        os.remove(dest)

    try:
        with open(dest, "xb") as handle:
            handle.write(buffer.getvalue())
    except FileExistsError as e:
        pass
