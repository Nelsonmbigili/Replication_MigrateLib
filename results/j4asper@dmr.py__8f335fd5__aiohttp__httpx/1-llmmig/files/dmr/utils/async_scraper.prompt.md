The following Python code currently uses the library "aiohttp" version 3.9.5.
Migrate this code to use the library "httpx" version 0.28.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "aiohttp" to "httpx".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "aiohttp" and "httpx".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from aiohttp import ClientSession
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


async def get_token(session) -> Tuple[str, str]:
    """Get dmrFormToken"""
    async with session.get("https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej", headers=get_headers(), allow_redirects=True) as resp:
        content = await resp.text()
    source = fromstring(content)
    token, url = get_token_and_url(source)
    return token, url


async def scrape_async(license_plate: str) -> Optional[dict]:

    async with ClientSession() as session:
        # Get dmrFormToken required to make site requests and get url to post data
        token, new_url = await get_token(session)

        payload = {
            "dmrFormToken": token,
            "soegeord": license_plate,
            "soegekriterie:": "REGISTRERINGSNUMMER",
            new_url: "Søg"
        }

        async with session.post('https://motorregister.skat.dk' + new_url, data=payload, headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url}), allow_redirects=True) as resp:
            content = await resp.text()

        if "Ingen køretøjer fundet." in content:
            # license plate doesn't exist
            return None

        # Page 1 scrape
        source = fromstring(content)
        data = page_1(source)

        new_url_without_last_16_chars = new_url[:-16]

        # Page 2 scrape
        async with session.get(str(resp.url) + "&_eventId=customPage&_pageIndex=1", headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url_without_last_16_chars}), allow_redirects=True) as resp:
            content = await resp.text()
        source = fromstring(content)
        data.update(page_2(source))

        # Page 4 scrape
        async with session.get(str(resp.url) + "&_eventId=customPage&_pageIndex=3", headers=get_headers({"Referer":"https://motorregister.skat.dk" + new_url_without_last_16_chars}), allow_redirects=True) as resp:
            content = await resp.text()
        if "Ingen forsikring" not in content:
            source = fromstring(content)
            data.update(page_4(source))
        else:
            data.update({"insurance": None})

    return data

```