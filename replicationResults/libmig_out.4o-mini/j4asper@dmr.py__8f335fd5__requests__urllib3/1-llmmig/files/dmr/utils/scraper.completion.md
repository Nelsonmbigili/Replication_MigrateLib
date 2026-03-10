### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Session Management**: The `Session` object from `requests` was replaced with a `PoolManager` from `urllib3`. This is because `urllib3` does not have a session concept like `requests`, but `PoolManager` can be used to manage connections.
  
2. **HTTP Methods**: The `get` and `post` methods from `requests` were replaced with `urlopen` for GET requests and `request` for POST requests in `urllib3`. The `urlopen` method is used for simple GET requests, while the `request` method is used for POST requests, where we can specify the method and the data.

3. **Response Handling**: The response from `urllib3` is handled differently. Instead of accessing `resp.text`, we use `resp.data.decode('utf-8')` to get the response body as a string.

4. **Headers**: The headers are passed as a dictionary directly in the `request` method for POST requests.

5. **Redirects**: The `allow_redirects` parameter is not needed in `urllib3` as it handles redirects automatically.

Here is the modified code:

```python
from urllib3 import PoolManager
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


def get_token(http) -> Tuple[str, str]:
    """Get dmrFormToken"""
    resp = http.request("GET", "https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej", headers=get_headers())
    source = fromstring(resp.data.decode('utf-8'))
    token, url = get_token_and_url(source)
    return token, url


def scrape(license_plate: str) -> Optional[dict]:

    http = PoolManager()
    # Get dmrFormToken required to make site requests and get url to post data
    token, new_url = get_token(http)

    payload = {
        "dmrFormToken": token,
        "soegeord": license_plate,
        "soegekriterie:": "REGISTRERINGSNUMMER",
        new_url: "Søg"
    }

    resp = http.request('POST', 'https://motorregister.skat.dk' + new_url, fields=payload, headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url}))

    if "Ingen køretøjer fundet." in resp.data.decode('utf-8'):
        # license plate doesn't exist
        return None

    # Page 1 scrape
    source = fromstring(resp.data.decode('utf-8'))
    data = page_1(source)

    # Page 2 scrape
    resp = http.request("GET", str(resp.url) + "&_eventId=customPage&_pageIndex=1", headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]}))
    source = fromstring(resp.data.decode('utf-8'))
    data.update(page_2(source))
    
    # Page 4 scrape
    resp = http.request("GET", str(resp.url) + "&_eventId=customPage&_pageIndex=3", headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]}))
    if "Ingen forsikring" not in resp.data.decode('utf-8'):
        source = fromstring(resp.data.decode('utf-8'))
        data.update(page_4(source))
    else:
        data.update({"insurance": None})

    return data
```