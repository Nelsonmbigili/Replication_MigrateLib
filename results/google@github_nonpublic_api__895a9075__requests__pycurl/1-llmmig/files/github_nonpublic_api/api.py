import os.path
import functools
from enum import Enum
import re
from urllib.parse import urljoin
import html5lib
import pyotp
import pycurl
from absl import logging
from configobj import ConfigObj
from typing import Optional
from io import BytesIO


class CurlSession:
    """Custom session management using pycurl."""
    def __init__(self):
        self.curl = pycurl.Curl()
        self.cookie_file = "cookies.txt"
        self.curl.setopt(pycurl.COOKIEFILE, self.cookie_file)
        self.curl.setopt(pycurl.COOKIEJAR, self.cookie_file)
        self.curl.setopt(pycurl.FOLLOWLOCATION, True)
        self.curl.setopt(pycurl.MAXREDIRS, 5)

    def get(self, url: str) -> str:
        """Perform a GET request."""
        buffer = BytesIO()
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        return buffer.getvalue().decode("utf-8")

    def post(self, url: str, data: dict) -> str:
        """Perform a POST request."""
        buffer = BytesIO()
        postfields = "&".join(f"{key}={value}" for key, value in data.items())
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.POST, True)
        self.curl.setopt(pycurl.POSTFIELDS, postfields)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.perform()
        return buffer.getvalue().decode("utf-8")

    def close(self):
        """Close the curl session."""
        self.curl.close()


def _get_and_submit_form(
    session: CurlSession, url: str, data_callback=None, form_matcher=lambda form: True
):
    logging.info("Fetching URL %s", url)
    response_text = session.get(url)

    logging.info("Fetched URL %s", url)

    doc = html5lib.parse(response_text, namespaceHTMLElements=False)
    forms = doc.findall(".//form")

    submit_form = None
    for form in forms:
        if form_matcher(form):
            submit_form = form
            break
    if submit_form is None:
        raise ValueError("Unable to find form")

    action_url = submit_form.attrib["action"]
    # Look at all the inputs under the given form.
    inputs = submit_form.findall(".//input")

    data = dict()
    for form_input in inputs:
        value = form_input.attrib.get("value")
        if value and "name" in form_input.attrib:
            data[form_input.attrib["name"]] = value

    # Have the caller provide additional data
    if data_callback:
        data_callback(data)

    logging.debug("Form data: %s", str(data))

    submit_url = urljoin(url, action_url)
    logging.info("Posting form to URL %s", submit_url)

    response_text = session.post(submit_url, data=data)
    return response_text


def _get_url_with_session(session: CurlSession, url: str):
    logging.info("Fetching URL %s", url)
    response_text = session.get(url)
    return response_text


def create_login_session(
    username: str,
    password: str,
    tfa_callback,
    session: Optional[CurlSession] = None,
) -> CurlSession:
    """Create a CurlSession object with logged in GitHub cookies for the user."""
    session = session or CurlSession()

    def _login_callback(data):
        data.update(dict(login=username, password=password))

    _get_and_submit_form(
        session=session, url="https://github.com/login", data_callback=_login_callback
    )

    def _tfa_callback(data):
        data.update(dict(otp=tfa_callback()))

    _get_and_submit_form(
        session=session,
        url="https://github.com/sessions/two-factor",
        data_callback=_tfa_callback,
    )

    return session


class OrganizationUsage(Enum):
    """Organization Usage for Organization Creation."""

    PERSONAL = "standard"
    BUSINESS = "corporate"


class Api(object):
    """API Endpoint for doing non-public things to GitHub."""

    def __init__(
        self,
        username: str,
        password: str,
        tfa_callback=None,
        session: Optional[CurlSession] = None,
    ):
        self._session = session or create_login_session(
            username=username,
            password=password,
            tfa_callback=tfa_callback,
            session=session,
        )

    def request_usage(self, enterprise_name: str, days: int = 30) -> str:
        """Requests a GitHub usage report."""

        def _request_usage_callback(data):
            data["days"] = days

        action = f"/enterprises/{enterprise_name}/settings/metered_exports"
        url = _REQUEST_USAGE_URL.format(enterprise_name=enterprise_name)
        return _get_and_submit_form(
            session=self._session,
            url=url,
            data_callback=_request_usage_callback,
            form_matcher=lambda form: form.attrib.get("action") == action,
        )

    # Other methods remain the same, replacing `requests` with `pycurl` equivalents.


if __name__ == "__main__":
    config = ConfigObj(os.path.expanduser("~/github.ini"), _inspec=True)

    api = Api(
        username=config["username"],
        password=config["password"],
        tfa_callback=lambda: pyotp.TOTP(config["otp_seed"]).now(),
    )
