### Explanation of Changes

To migrate the code from using the `requests` library to `pycurl`, the following changes were made:

1. **Session Management**: `requests.Session` was replaced with `pycurl.Curl`. Since `pycurl` does not have a session object, we manually set up and reuse a `pycurl.Curl` instance for each request.
2. **GET Requests**: The `session.get` calls were replaced with `pycurl` configurations for GET requests. This involves setting the URL, headers, and enabling redirects using `pycurl` options.
3. **POST Requests**: The `session.post` calls were replaced with `pycurl` configurations for POST requests. This includes setting the URL, headers, payload (as form data), and enabling redirects.
4. **Response Handling**: `pycurl` does not return a response object like `requests`. Instead, the response body is written to a buffer (e.g., `io.BytesIO`), which is then decoded to extract the response text.
5. **Headers**: Headers are set using the `pycurl.HTTPHEADER` option, and the `get_headers` function is used as before.
6. **Redirects**: Redirects are enabled using the `pycurl.FOLLOWLOCATION` option.
7. **Error Handling**: Basic error handling is added to ensure that `pycurl` operations are properly executed.

### Modified Code

```python
import pycurl
import io
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


def perform_request(curl: pycurl.Curl, url: str, method: str = "GET", headers: dict = None, data: dict = None) -> str:
    """Helper function to perform a request using pycurl."""
    buffer = io.BytesIO()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.FOLLOWLOCATION, True)

    if headers:
        curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

    if method == "POST" and data:
        curl.setopt(pycurl.POST, True)
        curl.setopt(pycurl.POSTFIELDS, "&".join(f"{key}={value}" for key, value in data.items()))
    else:
        curl.setopt(pycurl.POST, False)

    curl.perform()
    return buffer.getvalue().decode("utf-8")


def get_token(curl: pycurl.Curl) -> Tuple[str, str]:
    """Get dmrFormToken"""
    url = "https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej"
    headers = get_headers()
    response_text = perform_request(curl, url, headers=headers)
    source = fromstring(response_text)
    token, url = get_token_and_url(source)
    return token, url


def scrape(license_plate: str) -> Optional[dict]:
    curl = pycurl.Curl()

    try:
        # Get dmrFormToken required to make site requests and get url to post data
        token, new_url = get_token(curl)

        payload = {
            "dmrFormToken": token,
            "soegeord": license_plate,
            "soegekriterie:": "REGISTRERINGSNUMMER",
            new_url: "Søg"
        }

        post_url = 'https://motorregister.skat.dk' + new_url
        headers = get_headers({"Referer": "https://motorregister.skat.dk" + new_url})
        response_text = perform_request(curl, post_url, method="POST", headers=headers, data=payload)

        if "Ingen køretøjer fundet." in response_text:
            # license plate doesn't exist
            return None

        # Page 1 scrape
        source = fromstring(response_text)
        data = page_1(source)

        # Page 2 scrape
        page_2_url = str(post_url) + "&_eventId=customPage&_pageIndex=1"
        headers = get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]})
        response_text = perform_request(curl, page_2_url, headers=headers)
        source = fromstring(response_text)
        data.update(page_2(source))
        
        # Page 4 scrape
        page_4_url = str(post_url) + "&_eventId=customPage&_pageIndex=3"
        response_text = perform_request(curl, page_4_url, headers=headers)
        if "Ingen forsikring" not in response_text:
            source = fromstring(response_text)
            data.update(page_4(source))
        else:
            data.update({"insurance": None})

    finally:
        curl.close()

    return data
```

### Key Notes:
1. **`perform_request` Function**: This helper function centralizes the logic for making HTTP requests using `pycurl`. It handles GET and POST requests, headers, and response decoding.
2. **Session Replacement**: The `pycurl.Curl` instance is used in place of `requests.Session`. It is explicitly closed in the `finally` block to ensure proper resource cleanup.
3. **Payload Encoding**: For POST requests, the payload is manually encoded as a URL-encoded string since `pycurl` does not handle this automatically.
4. **Error Handling**: While basic error handling is included (e.g., closing the `pycurl.Curl` instance), additional error handling (e.g., for network errors) can be added if needed.