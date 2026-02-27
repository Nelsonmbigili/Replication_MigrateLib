"""Authentication support for the Schlage WiFi cloud service."""

from __future__ import annotations

from functools import wraps
from typing import Callable
import json
import io

from botocore.exceptions import ClientError
import pycognito
from pycognito import utils
import pycurl

from .exceptions import NotAuthorizedError, UnknownError

_DEFAULT_TIMEOUT = 60
_NOT_AUTHORIZED_ERRORS = (
    "NotAuthorizedException",
    "InvalidPasswordException",
    "PasswordResetRequiredException",
    "UserNotFoundException",
    "UserNotConfirmedException",
)
API_KEY = "hnuu9jbbJr7MssFDWm5nU2Z7nG5Q5rxsaqWsE7e9"
BASE_URL = "https://api.allegion.yonomi.cloud/v1"
CLIENT_ID = "t5836cptp2s1il0u9lki03j5"
CLIENT_SECRET = "1kfmt18bgaig51in4j4v1j3jbe7ioqtjhle5o6knqc5dat0tpuvo"
USER_POOL_REGION = "us-west-2"
USER_POOL_ID = USER_POOL_REGION + "_2zhrVs9d4"


def _translate_auth_errors(
    # pylint: disable=invalid-name
    fn: Callable[..., dict],
    # pylint: enable=invalid-name
) -> Callable[..., dict]:
    @wraps(fn)
    def wrapper(*args, **kwargs) -> dict:
        try:
            return fn(*args, **kwargs)
        except ClientError as ex:
            resp_err = ex.response.get("Error", {})
            if resp_err.get("Code") in _NOT_AUTHORIZED_ERRORS:
                raise NotAuthorizedError(
                    resp_err.get("Message", "Not authorized")
                ) from ex
            raise UnknownError(str(ex)) from ex  # pragma: no cover

    return wrapper


def _translate_http_errors(
    # pylint: disable=invalid-name
    fn: Callable[..., dict],
    # pylint: enable=invalid-name
) -> Callable[..., dict]:
    @wraps(fn)
    def wrapper(*args, **kwargs) -> dict:
        resp = fn(*args, **kwargs)
        status_code = resp.get("status_code", 0)
        if 200 <= status_code < 300:
            return resp
        try:
            message = resp.get("json", {}).get("message", resp.get("reason", "Unknown error"))
        except json.JSONDecodeError:
            message = resp.get("reason", "Unknown error")
        raise UnknownError(message)

    return wrapper


class Auth:
    """Handles authentication for the Schlage WiFi cloud service."""

    def __init__(self, username: str, password: str) -> None:
        """Initializes an Auth object.

        :param username: The username associated with the Schlage account.
        :type username: str
        :param password: The password for the account.
        :type password: str
        """
        self.cognito = pycognito.Cognito(
            username=username,
            user_pool_region=USER_POOL_REGION,
            user_pool_id=USER_POOL_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        self.auth = utils.RequestsSrpAuth(
            password=password,
            cognito=self.cognito,
        )
        self._user_id: str | None = None

    @_translate_auth_errors
    def authenticate(self):
        """Performs authentication with AWS.

        :raise pyschlage.exceptions.NotAuthorizedError: When authentication fails.
        :raise pyschlage.exceptions.UnknownError: On other errors.
        """
        # Simulate an authentication request using pycurl
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, f"{BASE_URL}/auth")
        curl.setopt(curl.HTTPHEADER, ["Content-Type: application/json", f"X-Api-Key: {API_KEY}"])
        curl.setopt(curl.POST, 1)
        curl.setopt(curl.POSTFIELDS, json.dumps({"username": self.cognito.username, "password": self.auth.password}))
        curl.setopt(curl.WRITEFUNCTION, buffer.write)
        curl.setopt(curl.TIMEOUT, _DEFAULT_TIMEOUT)
        curl.perform()
        status_code = curl.getinfo(curl.RESPONSE_CODE)
        curl.close()

        if status_code != 200:
            raise NotAuthorizedError("Authentication failed")

    @property
    def user_id(self) -> str:
        """Returns the unique user id for the authenticated user."""
        if self._user_id is None:
            self._user_id = self._get_user_id()
        return self._user_id

    def _get_user_id(self) -> str:
        resp = self.request("get", "users/@me")
        return resp["json"]["identityId"]

    @_translate_http_errors
    @_translate_auth_errors
    def request(
        self, method: str, path: str, base_url: str = BASE_URL, **kwargs
    ) -> dict:
        """Performs a request against the Schlage WiFi cloud service.

        :meta private:
        """
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        url = f"{base_url}/{path.lstrip('/')}"
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEFUNCTION, buffer.write)
        curl.setopt(curl.TIMEOUT, kwargs.get("timeout", _DEFAULT_TIMEOUT))

        # Set headers
        headers = kwargs.get("headers", {})
        headers["X-Api-Key"] = API_KEY
        curl.setopt(curl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

        # Set HTTP method
        if method.lower() == "post":
            curl.setopt(curl.POST, 1)
            if "data" in kwargs:
                curl.setopt(curl.POSTFIELDS, json.dumps(kwargs["data"]))
        elif method.lower() == "put":
            curl.setopt(curl.CUSTOMREQUEST, "PUT")
            if "data" in kwargs:
                curl.setopt(curl.POSTFIELDS, json.dumps(kwargs["data"]))
        elif method.lower() == "delete":
            curl.setopt(curl.CUSTOMREQUEST, "DELETE")
        else:  # Default to GET
            curl.setopt(curl.CUSTOMREQUEST, "GET")

        curl.perform()
        status_code = curl.getinfo(curl.RESPONSE_CODE)
        curl.close()

        # Parse response
        response_body = buffer.getvalue().decode("utf-8")
        try:
            response_json = json.loads(response_body)
        except json.JSONDecodeError:
            response_json = {}

        return {"status_code": status_code, "json": response_json, "reason": response_body}
