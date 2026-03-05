### Explanation of Changes
To migrate the code from using the `requests` library to the `pycurl` library, several changes were made:

1. **Importing PycURL**: The `requests` library was replaced with `pycurl`.
2. **Making GET Requests**: The `requests.get()` method was replaced with `pycurl.Curl()` to perform GET requests. This involves setting various options for the `Curl` object.
3. **Handling Responses**: Instead of directly accessing `response.json()` and `response.content`, we need to handle the response using a callback function to capture the output and then decode it appropriately.
4. **Error Handling**: The `raise_for_status()` method from `requests` was replaced with a manual check for HTTP errors using `curl.getinfo(pycurl.RESPONSE_CODE)`.

Here is the modified code:

```python
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
``` 

This code now uses `pycurl` to perform HTTP GET requests while maintaining the original structure and functionality of the code.