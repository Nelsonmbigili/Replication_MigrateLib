from typing import Any
import pycurl
from io import BytesIO
import json


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
    """
    Perform a GET request and return the JSON response.
    """
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.FOLLOWLOCATION, True)

    try:
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        if status_code >= 400:
            raise Exception(f"HTTP Error: {status_code} for URL: {url}")
    finally:
        curl.close()

    response_data = buffer.getvalue()
    return json.loads(response_data.decode("utf-8"))


def get_content(url: str) -> bytes:
    """
    Perform a GET request and return the raw content.
    """
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.FOLLOWLOCATION, True)

    try:
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        if status_code >= 400:
            raise Exception(f"HTTP Error: {status_code} for URL: {url}")
    finally:
        curl.close()

    return buffer.getvalue()
