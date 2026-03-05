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
