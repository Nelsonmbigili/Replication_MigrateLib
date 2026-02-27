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
