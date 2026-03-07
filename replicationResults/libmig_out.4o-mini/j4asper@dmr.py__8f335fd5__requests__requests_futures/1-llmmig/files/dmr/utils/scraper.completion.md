### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: Instead of importing `Session` from `requests`, we import `FuturesSession` from `requests_futures.sessions`.
2. **Session Initialization**: The `FuturesSession` allows for asynchronous requests, so we create an instance of `FuturesSession` instead of `Session`.
3. **Making Requests**: The `get` and `post` methods of `FuturesSession` return a `Future` object, which we need to call `.result()` on to get the actual response. This is done after making the requests.

Here is the modified code:

```python
from requests_futures.sessions import FuturesSession
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


def get_token(session) -> Tuple[str, str]:
    """Get dmrFormToken"""
    future = session.get("https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej", headers=get_headers(), allow_redirects=True)
    resp = future.result()
    source = fromstring(resp.text)
    token, url = get_token_and_url(source)
    return token, url


def scrape(license_plate: str) -> Optional[dict]:

    with FuturesSession() as session:
        # Get dmrFormToken required to make site requests and get url to post data
        token, new_url = get_token(session)

        payload = {
            "dmrFormToken": token,
            "soegeord": license_plate,
            "soegekriterie:": "REGISTRERINGSNUMMER",
            new_url: "Søg"
        }

        future = session.post('https://motorregister.skat.dk' + new_url, data=payload, headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url}), allow_redirects=True)
        resp = future.result()

        if "Ingen køretøjer fundet." in resp.text:
            # license plate doesn't exist
            return None

        # Page 1 scrape
        source = fromstring(resp.text)
        data = page_1(source)

        # Page 2 scrape
        future = session.get(str(resp.url) + "&_eventId=customPage&_pageIndex=1", headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url[:-16]}), allow_redirects=True)
        resp = future.result()
        source = fromstring(resp.text)
        data.update(page_2(source))
        
        # Page 4 scrape
        future = session.get(str(resp.url) + "&_eventId=customPage&_pageIndex=3", headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url[:-16]}), allow_redirects=True)
        resp = future.result()
        if "Ingen forsikring" not in resp.text:
            source = fromstring(resp.text)
            data.update(page_4(source))
        else:
            data.update({"insurance": None})

    return data
``` 

This code now uses `requests_futures` to handle asynchronous requests while maintaining the original structure and functionality.