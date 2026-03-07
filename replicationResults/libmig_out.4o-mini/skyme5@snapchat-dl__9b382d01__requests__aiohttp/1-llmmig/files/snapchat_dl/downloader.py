"""File Downlaoder for snapchat_dl."""
import os
import time
import aiohttp
import asyncio
from loguru import logger


async def download_url(url: str, dest: str, sleep_interval: int):
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
    await asyncio.sleep(sleep_interval)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        status=response.status,
                        message=response.reason
                    )

                if os.path.isfile(dest) and os.path.getsize(dest) == response.headers.get(
                    "content-length"
                ):
                    raise FileExistsError

                if os.path.isfile(dest) and os.path.getsize(dest) == 0:
                    os.remove(dest)

                with open(dest, "xb") as handle:
                    try:
                        while True:
                            data = await response.content.read(4194304)
                            if not data:
                                break
                            handle.write(data)
                    except aiohttp.ClientError as e:
                        logger.error(e)
        except FileExistsError as e:
            pass
