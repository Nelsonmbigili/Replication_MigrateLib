from typing import Any
import treq
from twisted.internet.defer import ensureDeferred


def build_route(base_url: str, *paths: str | int) -> str:
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    paths = tuple(str(p).strip("/") for p in paths)
    url = f"{base_url}/{'/'.join(paths)}"
    return url.strip("/")


def add_filters(url: str, *args: tuple[str, Any]) -> str:
    """
    Adds filters to the given url.
    """
    symbol = "?"
    if "?" in url:
        symbol = "&"
    for arg in args:
        url = f"{url}{symbol}{arg[0]}={arg[1]}"
        symbol = "&"
    return url


async def get(url: str) -> Any:
    response = await treq.get(url)
    if response.code >= 400:
        raise Exception(f"HTTP Error: {response.code}")
    return await response.json()


async def get_content(url: str) -> bytes:
    response = await treq.get(url)
    if response.code >= 400:
        raise Exception(f"HTTP Error: {response.code}")
    return await response.content()
