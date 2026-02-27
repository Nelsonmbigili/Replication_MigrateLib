from typing import Any, Dict, Generic, List, Union, cast
import pycurl
from io import BytesIO
import json
from typing_extensions import Literal, TypeVar

import resend
from resend.exceptions import NoContentError, raise_for_code_and_type
from resend.version import get_version

RequestVerb = Literal["get", "post", "put", "patch", "delete"]

T = TypeVar("T")


# Custom Response class to mimic requests.Response
class Response:
    def __init__(self, body: str, status_code: int, headers: Dict[str, str]):
        self._body = body
        self.status_code = status_code
        self.headers = headers

    @property
    def text(self) -> str:
        return self._body

    def json(self) -> Any:
        try:
            return json.loads(self._body)
        except json.JSONDecodeError:
            return None


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
            pycurl.error: If the request fails
        """
        resp = self.make_request(url=f"{resend.api_url}{self.path}")

        # delete calls do not return a body
        if resp.text == "" and resp.status_code == 200:
            return None

        # this is a safety net, if we get here it means the Resend API is having issues
        # and most likely the gateway is returning htmls
        if "application/json" not in resp.headers.get("content-type", ""):
            raise_for_code_and_type(
                code=500,
                message="Failed to parse Resend API response. Please try again.",
                error_type="InternalServerError",
            )

        # handle error in case there is a statusCode attr present
        # and status != 200 and response is a json.
        if resp.status_code != 200 and resp.json().get("statusCode"):
            error = resp.json()
            raise_for_code_and_type(
                code=error.get("statusCode"),
                message=error.get("message"),
                error_type=error.get("name"),
            )
        return cast(T, resp.json())

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

    def make_request(self, url: str) -> Response:
        """make_request is a helper function that makes the actual
        HTTP request to the Resend API.

        Args:
            url (str): The URL to make the request to

        Returns:
            Response: The response object from the request

        Raises:
            pycurl.error: If the request fails
        """
        headers = self.__get_headers()
        params = self.params
        verb = self.verb

        # Prepare buffers for response body and headers
        response_body = BytesIO()
        response_headers = BytesIO()

        # Initialize pycurl
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, response_body)
        curl.setopt(pycurl.HEADERFUNCTION, response_headers)

        # Set HTTP headers
        curl.setopt(
            pycurl.HTTPHEADER,
            [f"{key}: {value}" for key, value in headers.items()],
        )

        # Set HTTP method
        if verb == "post":
            curl.setopt(pycurl.POST, 1)
            curl.setopt(pycurl.POSTFIELDS, json.dumps(params))
        elif verb == "put":
            curl.setopt(pycurl.CUSTOMREQUEST, "PUT")
            curl.setopt(pycurl.POSTFIELDS, json.dumps(params))
        elif verb == "patch":
            curl.setopt(pycurl.CUSTOMREQUEST, "PATCH")
            curl.setopt(pycurl.POSTFIELDS, json.dumps(params))
        elif verb == "delete":
            curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")
        elif verb == "get":
            curl.setopt(pycurl.CUSTOMREQUEST, "GET")

        # Perform the request
        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            curl.close()
            raise e
        finally:
            curl.close()

        # Parse response body and headers
        body = response_body.getvalue().decode("utf-8")
        headers_raw = response_headers.getvalue().decode("utf-8")
        headers_dict = self._parse_headers(headers_raw)

        return Response(body=body, status_code=status_code, headers=headers_dict)

    def _parse_headers(self, headers_raw: str) -> Dict[str, str]:
        """Parses raw headers into a dictionary."""
        headers = {}
        for line in headers_raw.splitlines():
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value
        return headers
