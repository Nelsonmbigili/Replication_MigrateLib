from typing import Any, Dict, Generic, List, Union, cast

import treq
from typing_extensions import Literal, TypeVar

import resend
from resend.exceptions import NoContentError, raise_for_code_and_type
from resend.version import get_version

RequestVerb = Literal["get", "post", "put", "patch", "delete"]

T = TypeVar("T")


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

    async def perform(self) -> Union[T, None]:
        """Is the main function that makes the HTTP request
        to the Resend API. It uses the path, params, and verb attributes
        to make the request.

        Returns:
            Union[T, None]: A generic type of the Request class or None

        Raises:
            Exception: If the request fails
        """
        resp = await self.make_request(url=f"{resend.api_url}{self.path}")

        # delete calls do not return a body
        if await resp.text() == "" and resp.code == 200:
            return None

        # this is a safety net, if we get here it means the Resend API is having issues
        # and most likely the gateway is returning htmls
        content_type = resp.headers.getRawHeaders("content-type", [])
        if not any("application/json" in ct for ct in content_type):
            raise_for_code_and_type(
                code=500,
                message="Failed to parse Resend API response. Please try again.",
                error_type="InternalServerError",
            )

        # handle error in case there is a statusCode attr present
        # and status != 200 and response is a json.
        if resp.code != 200:
            error = await resp.json()
            if error.get("statusCode"):
                raise_for_code_and_type(
                    code=error.get("statusCode"),
                    message=error.get("message"),
                    error_type=error.get("name"),
                )
        return cast(T, await resp.json())

    async def perform_with_content(self) -> T:
        """
        Perform an HTTP request and return the response content.

        Returns:
            T: The content of the response

        Raises:
            NoContentError: If the response content is `None`.
        """
        resp = await self.perform()
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

    async def make_request(self, url: str) -> treq.response._Response:
        """make_request is a helper function that makes the actual
        HTTP request to the Resend API.

        Args:
            url (str): The URL to make the request to

        Returns:
            treq.response._Response: The response object from the request

        Raises:
            Exception: If the request fails
        """
        headers = self.__get_headers()
        params = self.params
        verb = self.verb

        try:
            response = await treq.request(verb, url, json=params, headers=headers)
            return response
        except Exception as e:
            raise e
