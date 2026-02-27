# SPDX-License-Identifier: Apache-2.0
"""DNS Authenticator for Infomaniak"""
import json
import logging
import idna
import pycurl
from io import BytesIO

from certbot import errors
from certbot.plugins import dns_common
try:
    import certbot.compat.os as os
except ImportError:
    import os

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for Infomaniak

    This plugin enables usage of Infomaniak public API to complete``dns-01`` challenges."""

    description = "Automates dns-01 challenges using Infomaniak API"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = ""
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=120
        )
        add("credentials", help="Infomaniak credentials INI file.")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return self.description

    def _setup_credentials(self):
        token = os.getenv("INFOMANIAK_API_TOKEN")
        if token is None:
            self.credentials = self._configure_credentials(
                "credentials",
                "Infomaniak credentials INI file",
                {
                    "token": "Infomaniak API token.",
                },
            )
            if not self.credentials:
                raise errors.PluginError("INFOMANIAK API Token not defined")
            self.token = self.credentials.conf("token")
        else:
            self.token = token

    def _perform(self, domain, validation_name, validation):
        decoded_domain = idna.decode(domain)
        try:
            self._api_client().add_txt_record(decoded_domain, validation_name, validation)
        except ValueError as err:
            raise errors.PluginError("Cannot add txt record: {err}".format(err=err))

    def _cleanup(self, domain, validation_name, validation):
        decoded_domain = idna.decode(domain)
        try:
            self._api_client().del_txt_record(decoded_domain, validation_name, validation)
        except ValueError as err:
            raise errors.PluginError("Cannot del txt record: {err}".format(err=err))

    def _api_client(self):
        return _APIDomain(self.token)


class _APIDomain:

    baseUrl = "https://api.infomaniak.com"

    def __init__(self, token):
        """Initialize class managing a domain within Infomaniak API

        :param str token: oauth2 token to consume Infomaniak API
        """
        self.token = token
        self.headers = ["Authorization: Bearer {token}".format(token=self.token)]

    def _make_request(self, method, url, payload=None):
        """Helper function to make HTTP requests using pycurl.

        :param str method: HTTP method (GET, POST, DELETE)
        :param str url: Full URL for the request
        :param dict payload: Optional payload for POST requests
        :returns: Parsed JSON response
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.HTTPHEADER, self.headers)
        curl.setopt(pycurl.WRITEDATA, buffer)

        if method == "POST":
            curl.setopt(pycurl.POST, 1)
            curl.setopt(pycurl.POSTFIELDS, json.dumps(payload))
            curl.setopt(pycurl.HTTPHEADER, self.headers + ["Content-Type: application/json"])
        elif method == "DELETE":
            curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            curl.close()
        except pycurl.error as e:
            raise errors.PluginError("Error in API request: {}".format(e))

        response = buffer.getvalue().decode("utf-8")
        try:
            result = json.loads(response)
        except json.JSONDecodeError as exc:
            raise errors.PluginError("No JSON in API response") from exc

        if result.get("result") == "success":
            return result.get("data")
        if result.get("error", {}).get("code") == "not_authorized":
            raise errors.PluginError("Cannot authenticate")
        raise errors.PluginError(
            "Error in API request: {} / {}".format(
                result.get("error", {}).get("code"), result.get("error", {}).get("description")
            )
        )

    def _get_request(self, url, payload=None):
        """Performs a GET request against API

        :param str url: relative url
        :param dict payload : body of request
        """
        if payload:
            query_string = "&".join(f"{key}={value}" for key, value in payload.items())
            url = f"{self.baseUrl}{url}?{query_string}"
        else:
            url = f"{self.baseUrl}{url}"
        logger.debug("GET %s", url)
        return self._make_request("GET", url)

    def _post_request(self, url, payload):
        """Performs a POST request

        :param str url: relative url
        :param dict payload : body of request
        """
        url = self.baseUrl + url
        logger.debug("POST %s", url)
        return self._make_request("POST", url, payload)

    def _delete_request(self, url):
        """Performs a DELETE request

        :param str url: relative url
        """
        url = self.baseUrl + url
        logger.debug("DELETE %s", url)
        return self._make_request("DELETE", url)

    # Other methods remain unchanged
