### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the import of `Session` from `requests` with `FuturesSession` from `requests_futures`.
2. **Session Replacement**: Replaced the `Session` object with `FuturesSession` to enable asynchronous requests.
3. **Handling Futures**: Since `requests_futures` returns a `Future` object for asynchronous requests, the `.result()` method is used to retrieve the actual response object where necessary.
4. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the existing application.

### Modified Code
```python
from requests_futures.sessions import FuturesSession
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers  # Assuming this is a custom module
from .extract_data import page_1, page_2, page_4, get_token_and_url  # Assuming this is a custom module


def get_token(session) -> Tuple[str, str]:
    """Get dmrFormToken"""
    future_resp = session.get("https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej", headers=get_headers(), allow_redirects=True)
    resp = future_resp.result()  # Wait for the response
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

        future_resp = session.post(
            'https://motorregister.skat.dk' + new_url,
            data=payload,
            headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url}),
            allow_redirects=True
        )
        resp = future_resp.result()  # Wait for the response

        if "Ingen køretøjer fundet." in resp.text:
            # license plate doesn't exist
            return None

        # Page 1 scrape
        source = fromstring(resp.text)
        data = page_1(source)

        # Page 2 scrape
        future_resp = session.get(
            str(resp.url) + "&_eventId=customPage&_pageIndex=1",
            headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]}),
            allow_redirects=True
        )
        resp = future_resp.result()  # Wait for the response
        source = fromstring(resp.text)
        data.update(page_2(source))
        
        # Page 4 scrape
        future_resp = session.get(
            str(resp.url) + "&_eventId=customPage&_pageIndex=3",
            headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]}),
            allow_redirects=True
        )
        resp = future_resp.result()  # Wait for the response
        if "Ingen forsikring" not in resp.text:
            source = fromstring(resp.text)
            data.update(page_4(source))
        else:
            data.update({"insurance": None})

    return data
```

### Key Points
- The `FuturesSession` object is used in place of `Session` to enable asynchronous requests.
- The `.result()` method is called on the `Future` object returned by `FuturesSession` methods (`get` and `post`) to retrieve the actual response.
- No other changes were made to the logic, structure, or style of the code to ensure compatibility with the rest of the application.