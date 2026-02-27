"""Authentication support for the Schlage WiFi cloud service."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from botocore.exceptions import ClientError
import pycognito
from pycognito import utils
import urllib3

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
    fn: Callable[..., urllib3.response.HTTPResponse],
    # pylint: enable=invalid-name
) -> Callable[..., urllib3.response.HTTPResponse]:
    @wraps(fn)
    def wrapper(*args, **kwargs) -> urllib3.response.HTTPResponse:
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
    fn: Callable[..., urllib3.response.HTTPResponse],
    # pylint: enable=invalid-name
) -> Callable[..., urllib3.response.HTTPResponse]:
    @wraps(fn)
    def wrapper(*args, **kwargs) -> urllib3.response.HTTPResponse:
        resp = fn(*args, **kwargs)
        if resp.status >= 400:
            try:
                message = resp.data.decode("utf-8")
            except ValueError:
                message = resp.reason
            raise UnknownError(message)
        return resp

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
        self.http = urllib3.PoolManager()

    @_translate_auth_errors
    def authenticate(self):
        """Performs authentication with AWS.

        :raise pyschlage.exceptions.NotAuthorizedError: When authentication fails.
        :raise pyschlage.exceptions.UnknownError: On other errors.
        """
        # Simulate a request for authentication
        self.auth(urllib3.request.Request())

    @property
    def user_id(self) -> str:
        """Returns the unique user id for the authenticated user."""
        if self._user_id is None:
            self._user_id = self._get_user_id()
        return self._user_id

    def _get_user_id(self) -> str:
        resp = self.request("get", "users/@me")
        return resp.data.decode("utf-8")["identityId"]

    @_translate_http_errors
    @_translate_auth_errors
    def request(
        self, method: str, path: str, base_url: str = BASE_URL, **kwargs
    ) -> urllib3.response.HTTPResponse:
        """Performs a request against the Schlage WiFi cloud service.

        :meta private:
        """
        kwargs["headers"] = kwargs.get("headers", {})
        kwargs["headers"]["X-Api-Key"] = API_KEY
        kwargs.setdefault("timeout", _DEFAULT_TIMEOUT)
        if "auth" in kwargs:
            del kwargs["auth"]  # urllib3 does not support `auth` directly
        url = f"{base_url}/{path.lstrip('/')}"
        return self.http.request(method.upper(), url, **kwargs)
