import treq
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


async def get_token() -> Tuple[str, str]:
    """Get dmrFormToken"""
    resp = await treq.get(
        "https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej",
        headers=get_headers()
    )
    source = fromstring(await resp.text())
    token, url = get_token_and_url(source)
    return token, url


async def scrape(license_plate: str) -> Optional[dict]:
    # Get dmrFormToken required to make site requests and get url to post data
    token, new_url = await get_token()

    payload = {
        "dmrFormToken": token,
        "soegeord": license_plate,
        "soegekriterie:": "REGISTRERINGSNUMMER",
        new_url: "Søg"
    }

    resp = await treq.post(
        'https://motorregister.skat.dk' + new_url,
        data=payload,
        headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url})
    )

    resp_text = await resp.text()
    if "Ingen køretøjer fundet." in resp_text:
        # license plate doesn't exist
        return None

    # Page 1 scrape
    source = fromstring(resp_text)
    data = page_1(source)

    # Page 2 scrape
    resp = await treq.get(
        str(resp.url) + "&_eventId=customPage&_pageIndex=1",
        headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]})
    )
    source = fromstring(await resp.text())
    data.update(page_2(source))
    
    # Page 4 scrape
    resp = await treq.get(
        str(resp.url) + "&_eventId=customPage&_pageIndex=3",
        headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]})
    )
    resp_text = await resp.text()
    if "Ingen forsikring" not in resp_text:
        source = fromstring(resp_text)
        data.update(page_4(source))
    else:
        data.update({"insurance": None})

    return data
