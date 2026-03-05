from typing import Any
import pycurl
from io import BytesIO

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
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, buffer)
    curl.perform()
    
    response_code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()
    
    if response_code != 200:
        raise Exception(f"HTTP error: {response_code}")
    
    return buffer.getvalue().decode('utf-8')


def get_content(url: str) -> bytes:
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, buffer)
    curl.perform()
    
    response_code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()
    
    if response_code != 200:
        raise Exception(f"HTTP error: {response_code}")
    
    return buffer.getvalue()
