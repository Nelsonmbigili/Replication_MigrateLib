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
