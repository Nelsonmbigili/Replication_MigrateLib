### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created a `FuturesSession` instance to handle asynchronous requests.
3. **Request Execution**: Updated the `make_request` method to use the `FuturesSession` instance for making requests. Since `requests_futures` returns a `Future` object, the `.result()` method is called to block and retrieve the response synchronously (to maintain the original synchronous behavior).
4. **Error Handling**: The error handling remains the same, as `requests_futures` is built on top of `requests` and raises the same exceptions.

### Modified Code
```python
from typing import Any, Dict, Generic, List, Union, cast

from requests_futures.sessions import FuturesSession
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
        self.session = FuturesSession()  # Initialize a FuturesSession for async requests

    def perform(self) -> Union[T, None]:
        """Is the main function that makes the HTTP request
        to the Resend API. It uses the path, params, and verb attributes
        to make the request.

        Returns:
            Union[T, None]: A generic type of the Request class or None

        Raises:
            requests.HTTPError: If the request fails
        """
        resp = self.make_request(url=f"{resend.api_url}{self.path}")

        # delete calls do not return a body
        if resp.text == "" and resp.status_code == 200:
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

    def make_request(self, url: str) -> Any:
        """make_request is a helper function that makes the actual
        HTTP request to the Resend API.

        Args:
            url (str): The URL to make the request to

        Returns:
            requests.Response: The response object from the request

        Raises:
            requests.HTTPError: If the request fails
        """
        headers = self.__get_headers()
        params = self.params
        verb = self.verb

        try:
            # Use the FuturesSession to make the request
            future = self.session.request(verb, url, json=params, headers=headers)
            return future.result()  # Block and get the response synchronously
        except Exception as e:
            raise e
```

### Key Points
- The `FuturesSession` is used to make asynchronous requests, but the `.result()` method ensures the behavior remains synchronous as in the original code.
- The rest of the code, including error handling and response processing, remains unchanged to preserve the original functionality.