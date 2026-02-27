import os.path
import functools
from enum import Enum
import re
from urllib.parse import urljoin

import html5lib
import pyotp
import aiohttp
from absl import logging
from configobj import ConfigObj
from typing import Optional


async def _get_and_submit_form(
    session, url: str, data_callback=None, form_matcher=lambda form: True
):
    logging.info("Fetching URL %s", url)
    async with session.get(url) as response:
        response.raise_for_status()
        logging.info("Fetching URL %s", response.url)
        for redirect_response in response.history:
            logging.info("Redirected from: %s", redirect_response.url)

        doc = html5lib.parse(await response.text(), namespaceHTMLElements=False)
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

        async with session.post(submit_url, data=data) as response:
            response.raise_for_status()
            return response


async def _get_url_with_session(session, url: str):
    logging.info("Fetching URL %s", url)
    async with session.get(url) as response:
        response.raise_for_status()
        return response


async def create_login_session(
    username: str,
    password: str,
    tfa_callback,
    session: Optional[aiohttp.ClientSession] = None,
) -> aiohttp.ClientSession:
    """Create an aiohttp.ClientSession object with logged in GitHub cookies for the user."""
    session = session or aiohttp.ClientSession()

    # Clear cookies before re-authentication
    session.cookie_jar.clear()

    def _login_callback(data):
        data.update(dict(login=username, password=password))

    await _get_and_submit_form(
        session=session, url="https://github.com/login", data_callback=_login_callback
    )

    def _tfa_callback(data):
        data.update(dict(otp=tfa_callback()))

    await _get_and_submit_form(
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
    """API Endpoint for doing non-public things to GitHub.

    Ideally these would all exist as REST API endpoints, but instead we get
    to pretend to be a real user.
    """

    def __init__(
        self,
        username: str,
        password: str,
        tfa_callback=None,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self._session = session

        async def init_session():
            self._session = await create_login_session(
                username=username,
                password=password,
                tfa_callback=tfa_callback,
                session=session,
            )

        import asyncio
        asyncio.run(init_session())

    async def request_usage(self, enterprise_name: str, days: int = 30) -> aiohttp.ClientResponse:
        """Requests a GitHub usage report.

        Github will send an email link when the report is available.
        """

        def _request_usage_callback(data):
            data["days"] = days

        action = f"/enterprises/{enterprise_name}/settings/metered_exports"
        url = _REQUEST_USAGE_URL.format(enterprise_name=enterprise_name)
        return await _get_and_submit_form(
            session=self._session,
            url=url,
            data_callback=_request_usage_callback,
            form_matcher=lambda form: form.attrib.get("action") == action,
        )

    async def create_organization(
        self,
        org_name: str,
        contact_email: str,
        org_usage: OrganizationUsage,
        business_name: Optional[str] = None,
    ) -> aiohttp.ClientResponse:
        """Create the specified GitHub organization.

        Right now, only creates free tier organizations.
        """

        def _create_org_callback(data):
            data["organization[profile_name]"] = org_name
            data["organization[login]"] = org_name
            data["organization[billing_email]"] = contact_email
            data["terms_of_service_type"] = org_usage.value
            data["agreed_to_terms"] = "yes"
            if org_usage == OrganizationUsage.BUSINESS:
                data["organization[company_name]"] = business_name

        return await _get_and_submit_form(
            session=self._session,
            url=_CREATE_ORG_URL,
            data_callback=_create_org_callback,
            form_matcher=lambda f: f.attrib.get("id") == "org-new-form",
        )


if __name__ == "__main__":
    import asyncio

    config = ConfigObj(os.path.expanduser("~/github.ini"), _inspec=True)

    async def main():
        api = Api(
            username=config["username"],
            password=config["password"],
            tfa_callback=lambda: pyotp.TOTP(config["otp_seed"]).now(),
        )
        # Example usage
        await api.request_usage(enterprise_name="example_enterprise")

    asyncio.run(main())
