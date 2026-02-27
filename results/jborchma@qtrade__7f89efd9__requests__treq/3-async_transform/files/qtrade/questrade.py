"""Core module for Questrade API wrapper."""

import logging
from typing import Any, Dict, List, Optional, Union

import treq
import yaml

from .utility import TokenDict, get_access_token_yaml, validate_access_token

log = logging.getLogger(__name__)  # pylint: disable=C0103

TOKEN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="


class Questrade:
    """Questrade baseclass.

    This class holds the methods to get access tokens, refresh access tokens as well as get
    stock quotes and portfolio overview. An instance of the class needs to be either initialized
    with an access_code or the path of a access token yaml file.

    Parameters
    ----------
    access_code: str, optional
        Access code from Questrade
    token_yaml: str, optional
        Path of the yaml-file holding the token payload
    save_yaml: bool, optional
        Boolean to indicate if the token payload will be saved in a yaml-file. Default True.
    """

    async def __init__(
        self,
        access_code: Optional[str] = None,
        token_yaml: Optional[str] = None,
        save_yaml: bool = True,
    ):
        self.access_token: TokenDict
        self.headers = None

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
            await self._get_access_token(save_yaml=save_yaml)

        self.account_id = None
        self.positions = None

    async def _send_message(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> Dict[str, Any]:  # pylint: disable=R0913
        """Send an API request.

        Parameters
        ----------
        method: str
            HTTP method (get, post, delete, etc.)
        endpoint: str
            Endpoint (to be added to base URL)
        params: dict, optional
            HTTP request parameters
        data: dict, optional
            JSON-encoded string payload for POST
        json: dict, optional
            Dictionary payload for POST

        Returns
        -------
        dict/list:
            JSON response
        """
        if self.access_token is not None:
            url = self.access_token["api_server"] + "/v1/" + endpoint
        else:
            log.error("Access token not set...")
            raise Exception("Access token not set...")

        response = await treq.request(
            method, url, params=params, data=data, json=json, headers=self.headers
        )
        response.raise_for_status()
        return await treq.json_content(response)

    def save_token_to_yaml(self, yaml_path: str = "access_token.yml"):
        """Save the token payload as a yaml-file.

        Parameters
        ----------
        yaml_path: str, optional
            Path of the yaml-file. If the file already exists, it will be overwritten. Defaults to
            access_token.yml
        """
        with open(yaml_path, "w") as yaml_file:
            log.debug("Saving access token to yaml file...")
            yaml.dump(self.access_token, yaml_file)

    async def _get_access_token(
        self, save_yaml: bool = False, yaml_path: str = "access_token.yml"
    ) -> TokenDict:
        """Get access token.

        This internal method gets the access token from the access code and optionally saves it in
        access_token.yaml.

        Parameters
        ----------
        save_yaml: bool, optional
            Boolean to indicate if the token payload will be saved in a yaml-file. Default False.
        yaml_path: str, optional
            Path of the yaml-file that will be saved. If the file already exists, it will be
            overwritten. Defaults to access_token.yml

        Returns
        -------
        dict
            Dict with the access token data.
        """
        url = TOKEN_URL + str(self.access_code)
        log.info("Getting access token...")
        response = await treq.get(url)
        response.raise_for_status()
        data = await treq.json_content(response)

        # validate response
        validate_access_token(**data)

        self.access_token = data

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

    async def refresh_access_token(
        self, from_yaml: bool = False, yaml_path: str = "access_token.yml"
    ) -> TokenDict:
        """Refresh access token.

        This method refreshes the access token. This only works if the overall access has not yet
        expired. By default it will look for the yaml-file, but it could also look for the internal
        state

        Parameters
        ----------
        from_yaml: bool, optional [False]
            This parameter controls if the refresh token is sourced from a yaml file
            or if the attribute `access_token` is used (default). If True, the yaml-file will be
            updated.
        yaml_path: str, optional
            Path of the yaml-file that will be updated. Defaults to access_token.yml

        Returns
        -------
        dict
            Dict with the access token data.
        """
        if from_yaml:
            old_access_token = get_access_token_yaml(yaml_path)
        else:
            old_access_token = self.access_token

        url = TOKEN_URL + str(old_access_token["refresh_token"])
        log.info("Refreshing access token...")
        response = await treq.get(url)
        response.raise_for_status()
        data = await treq.json_content(response)

        # validate response
        validate_access_token(**data)
        # set access token
        self.access_token = data

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

    # Other methods remain unchanged, except for replacing `requests` calls with `treq` calls
