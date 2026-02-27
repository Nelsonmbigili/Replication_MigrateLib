import pycurl
import io
from lxml.html import fromstring
from typing import Optional, Tuple
from .headers import get_headers
from .extract_data import page_1, page_2, page_4, get_token_and_url


def perform_request(curl: pycurl.Curl, url: str, method: str = "GET", headers: dict = None, data: dict = None) -> str:
    """Helper function to perform a request using pycurl."""
    buffer = io.BytesIO()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.FOLLOWLOCATION, True)

    if headers:
        curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

    if method == "POST" and data:
        curl.setopt(pycurl.POST, True)
        curl.setopt(pycurl.POSTFIELDS, "&".join(f"{key}={value}" for key, value in data.items()))
    else:
        curl.setopt(pycurl.POST, False)

    curl.perform()
    return buffer.getvalue().decode("utf-8")


def get_token(curl: pycurl.Curl) -> Tuple[str, str]:
    """Get dmrFormToken"""
    url = "https://motorregister.skat.dk/dmr-kerne/koeretoejdetaljer/visKoeretoej"
    headers = get_headers()
    response_text = perform_request(curl, url, headers=headers)
    source = fromstring(response_text)
    token, url = get_token_and_url(source)
    return token, url


def scrape(license_plate: str) -> Optional[dict]:
    curl = pycurl.Curl()

    try:
        # Get dmrFormToken required to make site requests and get url to post data
        token, new_url = get_token(curl)

        payload = {
            "dmrFormToken": token,
            "soegeord": license_plate,
            "soegekriterie:": "REGISTRERINGSNUMMER",
            new_url: "Søg"
        }

        post_url = 'https://motorregister.skat.dk' + new_url
        headers = get_headers({"Referer": "https://motorregister.skat.dk" + new_url})
        response_text = perform_request(curl, post_url, method="POST", headers=headers, data=payload)

        if "Ingen køretøjer fundet." in response_text:
            # license plate doesn't exist
            return None

        # Page 1 scrape
        source = fromstring(response_text)
        data = page_1(source)

        # Page 2 scrape
        page_2_url = str(post_url) + "&_eventId=customPage&_pageIndex=1"
        headers = get_headers({"Referer": "https://motorregister.skat.dk" + new_url[:-16]})
        response_text = perform_request(curl, page_2_url, headers=headers)
        source = fromstring(response_text)
        data.update(page_2(source))
        
        # Page 4 scrape
        page_4_url = str(post_url) + "&_eventId=customPage&_pageIndex=3"
        response_text = perform_request(curl, page_4_url, headers=headers)
        if "Ingen forsikring" not in response_text:
            source = fromstring(response_text)
            data.update(page_4(source))
        else:
            data.update({"insurance": None})

    finally:
        curl.close()

    return data
