"""Core module for Questrade API wrapper."""

import logging
from typing import Any, Dict, List, Optional, Union
import pycurl
import json
from io import BytesIO
import yaml

from .utility import TokenDict, get_access_token_yaml, validate_access_token

log = logging.getLogger(__name__)  # pylint: disable=C0103

TOKEN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="


class Questrade:
    """Questrade baseclass."""

    def __init__(
        self,
        access_code: Optional[str] = None,
        token_yaml: Optional[str] = None,
        save_yaml: bool = True,
    ):
        self.access_token: TokenDict
        self.headers = {}
        self.access_code = access_code
        self.token_yaml = token_yaml

        if access_code is None and self.token_yaml is not None:
            self.access_token = get_access_token_yaml(self.token_yaml)
            self.headers = {
                "Authorization": self.access_token["token_type"]
                + " "
                + self.access_token["access_token"]
            }
        else:
            self._get_access_token(save_yaml=save_yaml)

        self.account_id = None
        self.positions = None

    def _send_message(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> Dict[str, Any]:  # pylint: disable=R0913
        """Send an API request."""
        if self.access_token is not None:
            url = self.access_token["api_server"] + "/v1/" + endpoint
        else:
            log.error("Access token not set...")
            raise Exception("Access token not set...")

        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.setopt(pycurl.TIMEOUT, 30)
        curl.setopt(pycurl.CONNECTTIMEOUT, 10)

        # Set headers
        headers = [f"{key}: {value}" for key, value in self.headers.items()]
        curl.setopt(pycurl.HTTPHEADER, headers)

        # Set HTTP method
        if method.lower() == "get":
            curl.setopt(pycurl.HTTPGET, True)
        elif method.lower() == "post":
            curl.setopt(pycurl.POST, True)
            if json:
                curl.setopt(pycurl.POSTFIELDS, json.dumps(json))
            elif data:
                curl.setopt(pycurl.POSTFIELDS, data)
        elif method.lower() == "delete":
            curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")

        # Add query parameters
        if params:
            query_string = "&".join(f"{key}={value}" for key, value in params.items())
            curl.setopt(pycurl.URL, f"{url}?{query_string}")

        # Perform the request
        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            log.error(f"An error occurred: {e}")
            raise
        finally:
            curl.close()

        # Parse the response
        response_data = buffer.getvalue().decode("utf-8")
        buffer.close()

        if status_code >= 400:
            log.error(f"HTTP error {status_code}: {response_data}")
            raise Exception(f"HTTP error {status_code}: {response_data}")

        return json.loads(response_data)

    def save_token_to_yaml(self, yaml_path: str = "access_token.yml"):
        """Save the token payload as a yaml-file."""
        with open(yaml_path, "w") as yaml_file:
            log.debug("Saving access token to yaml file...")
            yaml.dump(self.access_token, yaml_file)

    def _get_access_token(
        self, save_yaml: bool = False, yaml_path: str = "access_token.yml"
    ) -> TokenDict:
        """Get access token."""
        url = TOKEN_URL + str(self.access_code)
        log.info("Getting access token...")
        response = self._send_message("get", url)

        # validate response
        validate_access_token(**response)

        self.access_token = response

        # clean the api_server entry of the escape characters
        self.access_token["api_server"] = self.access_token["api_server"].replace("\\", "")
        if self.access_token["api_server"][-1] == "/":
            self.access_token["api_server"] = self.access_token["api_server"][:-1]

        # set headers
        self.headers = {
            "Authorization": self.access_token["token_type"]
            + " "
            + self.access_token["access_token"]
        }

        # save access token
        if save_yaml:
            log.info("Saving yaml file to {}...".format(yaml_path))  # pylint: disable=W1202
            self.save_token_to_yaml(yaml_path=yaml_path)

        return self.access_token

    def refresh_access_token(
        self, from_yaml: bool = False, yaml_path: str = "access_token.yml"
    ) -> TokenDict:
        """Refresh access token."""
        if from_yaml:
            old_access_token = get_access_token_yaml(yaml_path)
        else:
            old_access_token = self.access_token

        url = TOKEN_URL + str(old_access_token["refresh_token"])
        log.info("Refreshing access token...")
        response = self._send_message("get", url)

        # validate response
        validate_access_token(**response)
        # set access token
        self.access_token = response

        # clean the api_server entry of the escape characters
        self.access_token["api_server"] = self.access_token["api_server"].replace("\\", "")
        if self.access_token["api_server"][-1] == "/":
            self.access_token["api_server"] = self.access_token["api_server"][:-1]

        # set headers
        self.headers = {
            "Authorization": self.access_token["token_type"]
            + " "
            + self.access_token["access_token"]
        }

        # save access token
        if from_yaml:
            self.save_token_to_yaml(yaml_path=yaml_path)

        return self.access_token

    def __del__(self):
        """Clean up resources."""
        pass
