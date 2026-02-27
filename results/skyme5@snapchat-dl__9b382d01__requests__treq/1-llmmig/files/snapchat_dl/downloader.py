"""File Downloader for snapchat_dl."""
import os
import time
import asyncio

import treq
from loguru import logger


async def download_url(url: str, dest: str, sleep_interval: int):
    """Download URL to destination path.

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

    try:
        response = await treq.get(url, timeout=10)
    except Exception as e:
        logger.error(f"Connection error: {e}")
        response = await treq.get(url, timeout=10)

    if response.code != 200:  # Equivalent to requests.codes.ok
        raise Exception(f"HTTP Error: {response.code}")

    content_length = response.headers.getRawHeaders("content-length")
    content_length = int(content_length[0]) if content_length else None

    if os.path.isfile(dest) and os.path.getsize(dest) == content_length:
        raise FileExistsError

    if os.path.isfile(dest) and os.path.getsize(dest) == 0:
        os.remove(dest)

    try:
        with open(dest, "xb") as handle:
            try:
                async def write_chunk(chunk):
                    handle.write(chunk)

                await treq.collect(response, write_chunk)
                handle.close()
            except Exception as e:
                logger.error(e)
    except FileExistsError as e:
        pass
