from typing import Any, Dict, Generic, List, Union, cast
import urllib3
import json
from urllib3.exceptions import HTTPError
from typing_extensions import Literal, TypeVar

import resend
from resend.exceptions import NoContentError, raise_for_code_and_type
from resend.version import get_version

RequestVerb = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]

T = TypeVar("T")

# Create a PoolManager instance
http = urllib3.PoolManager()

# This class wraps the HTTP request creation logic
class Request(Generic[T]):
    def __init__(
        self,
        path: str,
        params: Union[Dict[Any, Any], List[Dict[Any, Any]]],
        verb: RequestVerb,
    ):
        self.path = path
        self.params = params
        self.verb = verb

    def perform(self) -> Union[T, None]:
        """Is the main function that makes the HTTP request
        to the Resend API. It uses the path, params, and verb attributes
        to make the request.

        Returns:
            Union[T, None]: A generic type of the Request class or None

        Raises:
            HTTPError: If the request fails
        """
        resp = self.make_request(url=f"{resend.api_url}{self.path}")

        # delete calls do not return a body
        if resp.data == b"" and resp.status == 200:
            return None

        # this is a safety net, if we get here it means the Resend API is having issues
        # and most likely the gateway is returning htmls
        if "application/json" not in resp.headers["content-type"]:
            raise_for_code_and_type(
                code=500,
                message="Failed to parse Resend API response. Please try again.",
                error_type="InternalServerError",
            )

        # handle error in case there is a statusCode attr present
        # and status != 200 and response is a json.
        if resp.status != 200 and json.loads(resp.data).get("statusCode"):
            error = json.loads(resp.data)
            raise_for_code_and_type(
                code=error.get("statusCode"),
                message=error.get("message"),
                error_type=error.get("name"),
            )
        return cast(T, json.loads(resp.data))

    def perform_with_content(self) -> T:
        """
        Perform an HTTP request and return the response content.

        Returns:
            T: The content of the response

        Raises:
            NoContentError: If the response content is `None`.
        """
        resp = self.perform()
        if resp is None:
            raise NoContentError()
        return resp

    def __get_headers(self) -> Dict[Any, Any]:
        """get_headers returns the HTTP headers that will be
        used for every req.

        Returns:
            Dict: configured HTTP Headers
        """
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {resend.api_key}",
            "User-Agent": f"resend-python:{get_version()}",
        }

    def make_request(self, url: str) -> urllib3.response.HTTPResponse:
        """make_request is a helper function that makes the actual
        HTTP request to the Resend API.

        Args:
            url (str): The URL to make the request to

        Returns:
            urllib3.response.HTTPResponse: The response object from the request

        Raises:
            HTTPError: If the request fails
        """
        headers = self.__get_headers()
        params = self.params
        verb = self.verb

        try:
            return http.request(verb, url, json=params, headers=headers)
        except HTTPError as e:
            raise e
