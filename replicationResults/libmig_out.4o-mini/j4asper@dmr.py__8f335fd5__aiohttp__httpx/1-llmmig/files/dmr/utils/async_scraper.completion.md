### Explanation of Changes

To migrate the code from using the `aiohttp` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `aiohttp.ClientSession` to `httpx.AsyncClient`.
2. **Session Management**: Replaced `ClientSession` with `AsyncClient` for creating the session.
3. **Request Methods**: The `get` and `post` methods are now called directly on the `AsyncClient` instance instead of using the context manager with `async with`.
4. **Response Handling**: The response handling remains similar, but the way to access the response content is slightly different. The `text()` method is now called as `await resp.aread()` to read the response body.

Here is the modified code:

```python
from httpx import AsyncClient
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


async def get_token(session) -> Tuple[str, str]:
    """Get dmrFormToken"""
    async with session.get("https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej", headers=get_headers(), allow_redirects=True) as resp:
        content = await resp.aread()
    source = fromstring(content)
    token, url = get_token_and_url(source)
    return token, url


async def scrape_async(license_plate: str) -> Optional[dict]:

    async with AsyncClient() as session:
        # Get dmrFormToken required to make site requests and get url to post data
        token, new_url = await get_token(session)

        payload = {
            "dmrFormToken": token,
            "soegeord": license_plate,
            "soegekriterie:": "REGISTRERINGSNUMMER",
            new_url: "Søg"
        }

        async with session.post('https://motorregister.skat.dk' + new_url, data=payload, headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url}), allow_redirects=True) as resp:
            content = await resp.aread()

        if "Ingen køretøjer fundet." in content:
            # license plate doesn't exist
            return None

        # Page 1 scrape
        source = fromstring(content)
        data = page_1(source)

        new_url_without_last_16_chars = new_url[:-16]

        # Page 2 scrape
        async with session.get(str(resp.url) + "&_eventId=customPage&_pageIndex=1", headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url_without_last_16_chars}), allow_redirects=True) as resp:
            content = await resp.aread()
        source = fromstring(content)
        data.update(page_2(source))

        # Page 4 scrape
        async with session.get(str(resp.url) + "&_eventId=customPage&_pageIndex=3", headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url_without_last_16_chars}), allow_redirects=True) as resp:
            content = await resp.aread()
        if "Ingen forsikring" not in content:
            source = fromstring(content)
            data.update(page_4(source))
        else:
            data.update({"insurance": None})

    return data
```