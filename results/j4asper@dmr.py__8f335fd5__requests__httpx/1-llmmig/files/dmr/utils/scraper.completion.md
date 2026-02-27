### Explanation of Changes
To migrate the code from `requests` to `httpx`, the following changes were made:
1. **Session Replacement**: Replaced `requests.Session` with `httpx.Client`, which serves a similar purpose for managing sessions in `httpx`.
2. **Method Calls**: Updated `session.get` and `session.post` to use `httpx.Client`'s `get` and `post` methods. The method signatures are mostly the same, so minimal changes were required.
3. **Response Text**: Accessing the response body remains the same (`resp.text`), as `httpx` also provides this attribute.
4. **Headers**: The `headers` parameter works the same way in `httpx`, so no changes were needed there.
5. **Redirect Handling**: The `allow_redirects` parameter is supported in `httpx` as well, so it was directly reused.

### Modified Code
Here is the complete code after migrating to `httpx`:

```python
from httpx import Client
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers  # Assuming this is a custom function
from .extract_data import page_1, page_2, page_4, get_token_and_url


def get_token(session) -> Tuple[str, str]:
    """Get dmrFormToken"""
    resp = session.get("https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej", headers=get_headers(), allow_redirects=True)
    source = fromstring(resp.text)
    token, url = get_token_and_url(source)
    return token, url


def scrape(license_plate: str) -> Optional[dict]:

    with Client() as session:
        # Get dmrFormToken required to make site requests and get url to post data
        token, new_url = get_token(session)

        payload = {
            "dmrFormToken": token,
            "soegeord": license_plate,
            "soegekriterie:": "REGISTRERINGSNUMMER",
            new_url: "Søg"
        }

        resp = session.post('https://motorregister.skat.dk' + new_url, data=payload, headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url}), allow_redirects=True)

        if "Ingen køretøjer fundet." in resp.text:
            # license plate doesn't exist
            return None

        # Page 1 scrape
        source = fromstring(resp.text)
        data = page_1(source)

        # Page 2 scrape
        resp = session.get(str(resp.url) + "&_eventId=customPage&_pageIndex=1", headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url[:-16]}), allow_redirects=True)
        source = fromstring(resp.text)
        data.update(page_2(source))
        
        # Page 4 scrape
        resp = session.get(str(resp.url) + "&_eventId=customPage&_pageIndex=3", headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url[:-16]}), allow_redirects=True)
        if "Ingen forsikring" not in resp.text:
            source = fromstring(resp.text)
            data.update(page_4(source))
        else:
            data.update({"insurance": None})

    return data
```

### Key Notes
- The migration was straightforward because `httpx` is designed to be a drop-in replacement for `requests` in many cases.
- The `httpx.Client` object is used in the same way as `requests.Session`, and the method signatures for `get` and `post` are nearly identical.
- No changes were made to the logic, function names, or variable names to ensure compatibility with the rest of the application.