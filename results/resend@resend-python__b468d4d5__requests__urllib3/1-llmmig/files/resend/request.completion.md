### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Import Changes**: Removed the `requests` import and replaced it with `urllib3`.
2. **HTTP Request Handling**: Replaced `requests.request` with `urllib3.PoolManager` for making HTTP requests.
   - Created a `PoolManager` instance to manage connections.
   - Used the `request` method of `PoolManager` to perform HTTP requests.
3. **Response Handling**: Updated the response handling to work with `urllib3.response.HTTPResponse` instead of `requests.Response`.
   - Accessed the response body using `response.data` and decoded it to a string.
   - Checked the `Content-Type` header using `response.headers`.
   - Parsed JSON responses using `json.loads` from the `json` module.
4. **Error Handling**: Replaced `requests.HTTPError` with `urllib3.exceptions.HTTPError` for exception handling.
5. **Other Adjustments**: Updated the `make_request` method to handle the differences in how `urllib3` works compared to `requests`.

### Modified Code
```python
from typing import Any, Dict, Generic, List, Union, cast
import urllib3
import json
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
        self.http = urllib3.PoolManager()  # Create a PoolManager instance

    def perform(self) -> Union[T, None]:
        """Is the main function that makes the HTTP request
        to the Resend API. It uses the path, params, and verb attributes
        to make the request.

        Returns:
            Union[T, None]: A generic type of the Request class or None

        Raises:
            urllib3.exceptions.HTTPError: If the request fails
        """
        resp = self.make_request(url=f"{resend.api_url}{self.path}")

        # delete calls do not return a body
        if resp.data.decode("utf-8") == "" and resp.status == 200:
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
        if resp.status != 200:
            try:
                error = json.loads(resp.data.decode("utf-8"))
                if error.get("statusCode"):
                    raise_for_code_and_type(
                        code=error.get("statusCode"),
                        message=error.get("message"),
                        error_type=error.get("name"),
                    )
            except json.JSONDecodeError:
                pass  # If the response is not JSON, let it pass for now

        return cast(T, json.loads(resp.data.decode("utf-8")))

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
            urllib3.exceptions.HTTPError: If the request fails
        """
        headers = self.__get_headers()
        params = self.params
        verb = self.verb.upper()

        try:
            # Convert params to JSON string if it's a dictionary or list
            body = json.dumps(params) if params else None

            # Make the HTTP request using urllib3
            response = self.http.request(
                method=verb,
                url=url,
                body=body,
                headers=headers,
            )
            return response
        except urllib3.exceptions.HTTPError as e:
            raise e
```

### Key Points
- The `requests.request` method was replaced with `urllib3.PoolManager.request`.
- The `response` object is now an instance of `urllib3.response.HTTPResponse`, so its attributes (e.g., `data`, `status`, `headers`) were used instead of `requests.Response` attributes.
- JSON parsing was done using `json.loads` since `urllib3` does not have a built-in `.json()` method.
- Error handling was updated to use `urllib3.exceptions.HTTPError`.