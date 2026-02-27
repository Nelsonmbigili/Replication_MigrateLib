"""File Downlaoder for snapchat_dl."""
import os
import time

import httpx
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
        response = httpx.get(url, stream=True, timeout=10)
    except httpx.ConnectTimeout:
        response = httpx.get(url, stream=True, timeout=10)

    if response.status_code != httpx.codes.OK:
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
                for data in response.iter_bytes(chunk_size=4194304):
                    handle.write(data)
                handle.close()
            except httpx.RequestError as e:
                logger.error(e)
    except FileExistsError as e:
        pass
