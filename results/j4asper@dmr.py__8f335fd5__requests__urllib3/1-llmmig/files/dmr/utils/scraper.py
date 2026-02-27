from urllib3 import PoolManager
from urllib.parse import urlencode
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


def get_token(http) -> Tuple[str, str]:
    """Get dmrFormToken"""
    resp = http.request(
        "GET",
        "https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej",
        headers=get_headers()
    )
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

    encoded_payload = urlencode(payload)
    resp = http.request(
        "POST",
        'https://motorregister.skat.dk' + new_url,
        body=encoded_payload,
        headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url}),
    )

    if "Ingen køretøjer fundet." in resp.data.decode('utf-8'):
        # license plate doesn't exist
        return None

    # Page 1 scrape
    source = fromstring(resp.data.decode('utf-8'))
    data = page_1(source)

    # Page 2 scrape
    resp = http.request(
        "GET",
        str(resp.geturl()) + "&_eventId=customPage&_pageIndex=1",
        headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]}),
    )
    source = fromstring(resp.data.decode('utf-8'))
    data.update(page_2(source))
    
    # Page 4 scrape
    resp = http.request(
        "GET",
        str(resp.geturl()) + "&_eventId=customPage&_pageIndex=3",
        headers=get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]}),
    )
    if "Ingen forsikring" not in resp.data.decode('utf-8'):
        source = fromstring(resp.data.decode('utf-8'))
        data.update(page_4(source))
    else:
        data.update({"insurance": None})

    return data
