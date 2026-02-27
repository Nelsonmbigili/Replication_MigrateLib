"""File Downloader for snapchat_dl."""
import os
import time
import asyncio

import aiohttp
from loguru import logger


async def download_url(url: str, dest: str, sleep_interval: int):
    """Download URL to destination path.

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
    await asyncio.sleep(sleep_interval)

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        status=response.status, message="Request failed"
                    )

                content_length = response.headers.get("Content-Length")
                if os.path.isfile(dest) and os.path.getsize(dest) == int(content_length):
                    raise FileExistsError

                if os.path.isfile(dest) and os.path.getsize(dest) == 0:
                    os.remove(dest)

                try:
                    with open(dest, "xb") as handle:
                        try:
                            async for data in response.content.iter_chunked(4194304):
                                handle.write(data)
                            handle.close()
                        except aiohttp.ClientError as e:
                            logger.error(e)
                except FileExistsError as e:
                    pass
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
