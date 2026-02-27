### Explanation of Changes
To migrate the code from `aiohttp` to `httpx`, the following changes were made:
1. Replaced `aiohttp.ClientSession` with `httpx.AsyncClient`.
2. Updated the `session.get` and `session.post` calls to use `httpx.AsyncClient` methods (`client.get` and `client.post`).
3. Removed the `allow_redirects` parameter, as `httpx` follows redirects by default.
4. Updated the way response content is accessed:
   - In `aiohttp`, `resp.text()` is an `await`able coroutine.
   - In `httpx`, `resp.text` is a property (not `await`able).
5. Updated the `resp.url` attribute:
   - In `aiohttp`, `resp.url` is an `yarl.URL` object.
   - In `httpx`, `resp.url` is a `httpx.URL` object, but it can be used similarly as a string.

### Modified Code
```python
from httpx import AsyncClient
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


async def get_token(client) -> Tuple[str, str]:
    """Get dmrFormToken"""
    async with client.get("https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej", headers=get_headers()) as resp:
        content = resp.text
    source = fromstring(content)
    token, url = get_token_and_url(source)
    return token, url


async def scrape_async(license_plate: str) -> Optional[dict]:

    async with AsyncClient() as client:
        # Get dmrFormToken required to make site requests and get url to post data
        token, new_url = await get_token(client)

        payload = {
            "dmrFormToken": token,
            "soegeord": license_plate,
            "soegekriterie:": "REGISTRERINGSNUMMER",
            new_url: "Søg"
        }

        async with client.post('https://motorregister.skat.dk' + new_url, data=payload, headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url})) as resp:
            content = resp.text

        if "Ingen køretøjer fundet." in content:
            # license plate doesn't exist
            return None

        # Page 1 scrape
        source = fromstring(content)
        data = page_1(source)

        new_url_without_last_16_chars = new_url[:-16]

        # Page 2 scrape
        async with client.get(str(resp.url) + "&_eventId=customPage&_pageIndex=1", headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url_without_last_16_chars})) as resp:
            content = resp.text
        source = fromstring(content)
        data.update(page_2(source))

        # Page 4 scrape
        async with client.get(str(resp.url) + "&_eventId=customPage&_pageIndex=3", headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url_without_last_16_chars})) as resp:
            content = resp.text
        if "Ingen forsikring" not in content:
            source = fromstring(content)
            data.update(page_4(source))
        else:
            data.update({"insurance": None})

    return data
```

### Key Points
- `aiohttp.ClientSession` was replaced with `httpx.AsyncClient`.
- `resp.text()` (awaitable in `aiohttp`) was replaced with `resp.text` (property in `httpx`).
- `allow_redirects` was removed because `httpx` handles redirects by default.
- The rest of the code remains unchanged to ensure compatibility with the larger application.