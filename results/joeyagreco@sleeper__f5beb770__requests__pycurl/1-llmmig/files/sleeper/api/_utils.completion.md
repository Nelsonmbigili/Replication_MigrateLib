### Explanation of Changes

To migrate the code from using the `requests` library to `pycurl`, the following changes were made:

1. **Replaced `requests.get` with `pycurl`**:
   - `pycurl` requires setting up a `pycurl.Curl` object and configuring it with options such as the URL, HTTP method, and response handling.
   - The response data is captured using a `BytesIO` object from the `io` module.

2. **Error Handling**:
   - `pycurl` does not have a built-in `raise_for_status` method like `requests`. Instead, we manually check the HTTP status code and raise an exception if it indicates an error.

3. **Response Parsing**:
   - For JSON responses, the `BytesIO` content is decoded and parsed using the `json` module.
   - For binary content, the raw `BytesIO` content is returned.

4. **Removed `requests` Import**:
   - The `requests` library import was removed since it is no longer used.

Below is the modified code.

---

### Modified Code

```python
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
```

---

### Key Notes:
- The `pycurl.Curl` object is used to configure and execute HTTP requests.
- The `BytesIO` object is used to capture the response data.
- Error handling is implemented by checking the HTTP status code manually.
- The `json` module is used to parse JSON responses, as `pycurl` does not provide built-in JSON handling.
- The overall structure and function names remain unchanged to ensure compatibility with the rest of the application.