### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created an instance of `FuturesSession` to handle asynchronous requests.
3. **Request Handling**: Updated the `requests.post` and `requests.get` calls to use the `FuturesSession` instance. Since `requests_futures` returns a `Future` object, the `.result()` method is used to block and retrieve the response synchronously (to maintain the original synchronous behavior).
4. **Timeout Handling**: Passed the `timeout` parameter to the `.result()` method to ensure the timeout behavior remains consistent.

These changes ensure the code uses `requests_futures` while preserving the original synchronous behavior.

---

### Modified Code:
```python
"""
This is a simple representation of a token, which also renews automatically
if it expired.
"""

import logging
from typing import Optional
from requests_futures.sessions import FuturesSession
import jwt
from coguard_cli.auth import auth_config, util

COGUARD_REALM_TOKEN_URL = "/realms/coguard/protocol/openid-connect/token"

class Token():
    """
    A simple representation of an access token.
    """

    def __init__(self, token: str, inp_auth_config: auth_config.CoGuardCliConfig):
        """
        Initialization of this object with a valid token,
        and an auth_config in case we need to renew it.
        """
        self._token = token
        self._auth_config = inp_auth_config
        self._session = FuturesSession()  # Initialize FuturesSession for async requests

    def authenticate_to_server(self) -> Optional[str]:
        """
        This is the function which tries to make the call to the coguard authentication server.
        Returns None if authentication could not have been done, and the auth token otherwise.
        """
        if self._auth_config is None:
            self._token = None
            return None
        # The following check is just for the case if people use a different authentication
        # server url and forget the auth in the subpath
        if self._auth_config.get_auth_url().endswith('/auth'):
            complete_request_url = self._auth_config.get_auth_url() + COGUARD_REALM_TOKEN_URL
        else:
            complete_request_url = \
                f"{self._auth_config.get_auth_url()}/auth{COGUARD_REALM_TOKEN_URL}"
        token_request_future = self._session.post(
            complete_request_url,
            data={
                'client_id': 'client-react-frontend',
                'username': self._auth_config.get_username(),
                'password': self._auth_config.get_password(),
                'grant_type': 'password'
            }
        )
        token_request = token_request_future.result(timeout=300)  # Block and get the response
        if token_request.status_code != 200:
            logging.error("There was an error requesting the authentication token: %s",
                          token_request.reason)
            self._token = None
            return None
        response_json = token_request.json()
        if response_json.get("access_token", None) is None:
            self._token = None
            return None
        return_val = response_json.get("access_token", None)
        self._token = return_val
        return return_val

    def get_token(self, renewal=True) -> str:
        """
        Getter function for the token, which also renews in case the token has expired.
        """
        if renewal and self.is_token_expired():
            logging.debug("Token has expired. Renewing.")
            self._token = self.authenticate_to_server()
        return self._token

    def is_token_expired(self) -> bool:
        """
        Helper function to detect if a given token is expired or not.
        """
        public_key = self.get_public_key()
        if not public_key:
            logging.error(
                "Assuming free account, as we could not find the public key of the auth server."
            )
            return False
        try:
            self.get_decoded_jwt_token(public_key)
        except jwt.exceptions.JWTDecodeError:
            logging.debug("JWT token expired. Renewing.")
            return True
        return False

    def get_public_key(self) -> Optional[str]:
        """
        A helper function to retrieve the public key from the authentication server.
        Returns None if there is no public key.
        """
        if self._auth_config.get_auth_url().endswith('/auth'):
            complete_request_url = self._auth_config.get_auth_url() + "/realms/coguard"
        else:
            complete_request_url = f"{self._auth_config.get_auth_url()}/auth/realms/coguard"
        public_key_request_future = self._session.get(complete_request_url)
        public_key_request = public_key_request_future.result(timeout=5)  # Block and get the response
        if public_key_request.status_code != 200:
            logging.error("Could not retrieve public key from coguard url: %s",
                          str(public_key_request))
            logging.error("Assuming free account")
            return None
        response_json = public_key_request.json()
        public_key = response_json.get("public_key", "")
        if not public_key:
            logging.error("Could not extract public key.")
            return None
        logging.debug("The public key is %s", str(public_key))
        return public_key


    def get_decoded_jwt_token(self, public_key: str) -> jwt.jwk.AbstractJWKBase:
        """
        Helper function to get a decoded JWT token.
        """
        expanded_pkey = f"""-----BEGIN PUBLIC KEY-----
        {public_key}
        -----END PUBLIC KEY-----""".replace("        ", "")
        jwt_obj = jwt.JWT()
        logging.debug("Attempting to decode %s with public key %s",
                      self._token,
                      expanded_pkey)
        return jwt_obj.decode(self._token, jwt.jwk_from_pem(expanded_pkey.encode()))

    def extract_organization_from_token(self) -> Optional[str]:
        """
        This is the helper function to extract the organization from the token.
        Returning None if there is no organization.
        """
        public_key = self.get_public_key()
        if not public_key:
            return None
        jwt_decoded = self.get_decoded_jwt_token(public_key)
        org_result = jwt_decoded.get("organization", None)
        if isinstance(org_result, str):
            return org_result
        if isinstance(org_result, list) and len(org_result) > 0:
            if len(org_result) == 1:
                return org_result[0]
            input_val = None
            print("Multiple organizations detected:")
            print("\n".join(org for org in org_result))
            while input_val not in org_result:
                input_val = input(
                    f"Please type the organization you wish to use (default: {org_result[0]})"
                )
                if not input_val.strip():
                    input_val = org_result[0]
                if input_val not in org_result:
                    print("You typed in an invalid organization. Please repeat.")
            if input_val not in org_result:
                return None
            return input_val
        return None

    def extract_deal_type_from_token(
            self
    ) -> util.DealEnum:
        """
        This function uses a token, and a configuruation object, and extracts the deal
        type of the account stored in the JWT token.
        """
        # Getting the public key
        public_key = self.get_public_key()
        if not public_key:
            logging.error(
                "Assuming free account, as we could not find the public key of the auth server."
            )
            return util.DealEnum.FREE
        jwt_decoded = self.get_decoded_jwt_token(public_key)
        deal_identifiers = jwt_decoded.get('realm_access', {}).get('roles', [])
        for deal_enum in list(util.DealEnum):
            if deal_enum.value.upper() in deal_identifiers:
                return deal_enum
        logging.debug("No valid deal enum in decoded JWT token. Assuming free: %s",
                      str(jwt_decoded))
        return util.DealEnum.FREE
```

---

### Summary of Changes:
- Replaced `requests.post` and `requests.get` with `FuturesSession.post` and `FuturesSession.get`.
- Used `.result(timeout=...)` to block and retrieve the response synchronously.
- Introduced a `FuturesSession` instance (`self._session`) for making asynchronous requests.