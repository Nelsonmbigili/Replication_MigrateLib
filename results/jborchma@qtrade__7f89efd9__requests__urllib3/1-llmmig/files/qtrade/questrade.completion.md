### Explanation of Changes
To migrate the code from the `requests` library to `urllib3`, the following changes were made:
1. **Session Management**: Replaced `requests.Session` with `urllib3.PoolManager` for managing HTTP connections.
2. **HTTP Requests**: Replaced `requests.get`, `requests.post`, and `session.request` with `urllib3.PoolManager` methods (`request` for general requests, `request('GET', ...)` for GET requests, and `request('POST', ...)` for POST requests).
3. **Timeouts**: Added `timeout` as a parameter to `urllib3` requests since it is not directly part of the `PoolManager` configuration.
4. **Response Handling**: Replaced `resp.raise_for_status()` with manual status code checks (`if resp.status != 200: ...`) since `urllib3` does not have a built-in method for raising exceptions on HTTP errors.
5. **JSON Parsing**: Replaced `resp.json()` with `json.loads(resp.data.decode('utf-8'))` since `urllib3` does not have a built-in JSON parser.
6. **Session Closing**: Ensured the `PoolManager` is closed in the `__del__` method to release resources.

### Modified Code
Below is the entire code after migration to `urllib3`:

```python
"""Core module for Questrade API wrapper."""

import logging
import json
from typing import Any, Dict, List, Optional, Union

import urllib3
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

    def __init__(
        self,
        access_code: Optional[str] = None,
        token_yaml: Optional[str] = None,
        save_yaml: bool = True,
    ):
        self.access_token: TokenDict
        self.headers = None
        self.session = urllib3.PoolManager()

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

        headers = self.headers
        body = None
        if json:
            body = json.dumps(json)
            headers["Content-Type"] = "application/json"

        resp = self.session.request(
            method.upper(),
            url,
            fields=params,
            body=body,
            headers=headers,
            timeout=30,
        )

        if resp.status != 200:
            log.error(f"HTTP error {resp.status}: {resp.data.decode('utf-8')}")
            raise Exception(f"HTTP error {resp.status}: {resp.data.decode('utf-8')}")

        return json.loads(resp.data.decode("utf-8"))

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
        resp = self.session.request("GET", url, timeout=30)

        if resp.status != 200:
            log.error(f"HTTP error {resp.status}: {resp.data.decode('utf-8')}")
            raise Exception(f"HTTP error {resp.status}: {resp.data.decode('utf-8')}")

        response = json.loads(resp.data.decode("utf-8"))

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
        resp = self.session.request("GET", url, timeout=30)

        if resp.status != 200:
            log.error(f"HTTP error {resp.status}: {resp.data.decode('utf-8')}")
            raise Exception(f"HTTP error {resp.status}: {resp.data.decode('utf-8')}")

        response = json.loads(resp.data.decode("utf-8"))

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
        """Close session when class instance is deleted."""
        self.session.clear()
```

This code replaces all `requests` functionality with `urllib3` equivalents while maintaining the original structure and functionality.