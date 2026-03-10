from typing import Any
import urllib3
import json

http = urllib3.PoolManager()

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


def get(url: str) -> Any:
    response = http.request('GET', url)
    response.raise_for_status()
    return json.loads(response.data)


def get_content(url: str) -> bytes:
    response = http.request('GET', url)
    response.raise_for_status()
    return response.data
