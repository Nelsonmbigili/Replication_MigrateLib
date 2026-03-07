import pycurl
from io import BytesIO
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


def get_token() -> Tuple[str, str]:
    """Get dmrFormToken"""
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, "https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej")
    c.setopt(c.HTTPHEADER, get_headers())
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()

    body = buffer.getvalue().decode('utf-8')
    source = fromstring(body)
    token, url = get_token_and_url(source)
    return token, url


def scrape(license_plate: str) -> Optional[dict]:

    # Get dmrFormToken required to make site requests and get url to post data
    token, new_url = get_token()

    payload = {
        "dmrFormToken": token,
        "soegeord": license_plate,
        "soegekriterie:": "REGISTRERINGSNUMMER",
        new_url: "Søg"
    }

    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://motorregister.skat.dk' + new_url)
    c.setopt(c.POSTFIELDS, '&'.join([f"{key}={value}" for key, value in payload.items()]))
    c.setopt(c.HTTPHEADER, get_headers({"Referer": "https://motorregister.skat.dk" + new_url}))
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    response_body = buffer.getvalue().decode('utf-8')
    c.close()

    if "Ingen køretøjer fundet." in response_body:
        # license plate doesn't exist
        return None

    # Page 1 scrape
    source = fromstring(response_body)
    data = page_1(source)

    # Page 2 scrape
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, str(c.getinfo(c.EFFECTIVE_URL)) + "&_eventId=customPage&_pageIndex=1")
    c.setopt(c.HTTPHEADER, get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]}))
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    response_body = buffer.getvalue().decode('utf-8')
    c.close()

    source = fromstring(response_body)
    data.update(page_2(source))
    
    # Page 4 scrape
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, str(c.getinfo(c.EFFECTIVE_URL)) + "&_eventId=customPage&_pageIndex=3")
    c.setopt(c.HTTPHEADER, get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]}))
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    response_body = buffer.getvalue().decode('utf-8')
    c.close()

    if "Ingen forsikring" not in response_body:
        source = fromstring(response_body)
        data.update(page_4(source))
    else:
        data.update({"insurance": None})

    return data
