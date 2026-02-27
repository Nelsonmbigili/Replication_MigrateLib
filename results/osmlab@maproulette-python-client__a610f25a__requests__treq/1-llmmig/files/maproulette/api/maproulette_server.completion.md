### Explanation of Changes:
To migrate the code from the `requests` library to the `treq` library, the following changes were made:
1. **Session Handling**: `treq` does not use sessions like `requests.Session`. Instead, it uses `treq.request` or other specific methods (`treq.get`, `treq.post`, etc.) for each request. The session-related code was removed.
2. **Asynchronous Nature**: `treq` is built on top of `Twisted` and is asynchronous. All methods that make HTTP requests were converted to asynchronous methods using `async def` and `await`.
3. **Response Handling**: `treq` responses are asynchronous, so methods like `response.json()` and `response.text` were replaced with their asynchronous counterparts (`await response.json()` and `await response.text()`).
4. **Error Handling**: `treq` does not raise exceptions like `requests` for HTTP errors. Instead, the status code must be checked manually. The `raise_for_status` logic was replaced with explicit status code checks.
5. **Imports**: The `requests` import was replaced with `treq`.

Below is the modified code:

---

### Modified Code:
```python
"""This module contains the basic methods that handle API calls to the MapRoulette API. It uses the treq library to
accomplish this."""

import treq
import json
import time
from twisted.internet import defer
from .errors import HttpError, InvalidJsonError, ConnectionUnavailableError, UnauthorizedError, NotFoundError


class MapRouletteServer:
    """Class that holds the basic requests that can be made to the MapRoulette API."""
    def __init__(self, configuration):
        self.url = configuration.api_url
        self.base_url = configuration.base_url
        self.headers = configuration.headers
        self.certs = configuration.certs
        self.verify = configuration.verify
        if self.__check_health():
            self.headers = self.headers

    def __check_health(self, retries=3, delay=5):
        """Checks health of connection to host by pinging the URL set in the configuration

        :param retries: the number of retries to use to successfully ping the URL. Default is 3
        :param delay: the number of seconds to wait between retries
        :returns: True if GET request to ping endpoint is successful
        """
        for i in range(retries):
            try:
                response = defer.ensureDeferred(
                    treq.get(
                        self.base_url + '/ping',
                        headers=self.headers,
                        verify=self.verify,
                        cert=self.certs
                    )
                )
                if response.code != 200:
                    print(f"Unsuccessful connection. Retrying in {str(delay)} seconds")
                    time.sleep(delay)
                else:
                    return True
            except Exception:
                print(f"Connection not available. Attempt {str(i+1)} out of {str(retries)}")
                time.sleep(delay)

        raise ConnectionUnavailableError(
            message='Specified server unavailable'
        )

    async def get(self, endpoint, params=None):
        """Method that completes a GET request to the MapRoulette API

        :param endpoint: the server endpoint to use for the GET request
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = await treq.get(
            self.url + endpoint,
            params=params,
            headers=self.headers
        )
        if response.code == 404:
            raise NotFoundError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        elif response.code >= 400:
            raise HttpError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        try:
            return {
                "data": await response.json(),
                "status": response.code
            }
        except ValueError:
            return {
                "data": await response.text(),
                "status": response.code
            }

    async def post(self, endpoint, body=None, params=None):
        """Method that completes a POST request to the MapRoulette API

        :param endpoint: the server endpoint to use for the POST request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = await treq.post(
            self.url + endpoint,
            params=params,
            json=body,
            headers=self.headers
        )
        if response.code == 400:
            raise InvalidJsonError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        elif response.code == 401:
            raise UnauthorizedError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        elif response.code >= 400:
            raise HttpError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        try:
            return {
                "data": await response.json(),
                "status": response.code
            }
        except ValueError:
            return {
                "data": await response.text(),
                "status": response.code
            }

    async def put(self, endpoint, body=None, params=None):
        """Method that completes a PUT request to the MapRoulette API

        :param endpoint: the server endpoint to use for the PUT request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = await treq.put(
            self.url + endpoint,
            params=params,
            json=body,
            headers=self.headers
        )
        if response.code == 400:
            raise InvalidJsonError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        elif response.code == 401:
            raise UnauthorizedError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        elif response.code >= 400:
            raise HttpError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        try:
            return {
                "data": await response.json(),
                "status": response.code
            }
        except ValueError:
            return {
                "data": await response.text(),
                "status": response.code
            }

    async def delete(self, endpoint, params=None):
        """Method that completes a DELETE request to the MapRoulette API

        :param endpoint: the server endpoint to use for the DELETE request
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = await treq.delete(
            self.url + endpoint,
            params=params,
            headers=self.headers
        )
        if response.code == 401:
            raise UnauthorizedError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        elif response.code == 404:
            raise NotFoundError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        elif response.code >= 400:
            raise HttpError(
                message=await self.parse_response_message(response),
                status=response.code
            )
        try:
            return {
                "data": await response.json(),
                "status": response.code
            }
        except ValueError:
            return {
                "data": await response.text(),
                "status": response.code
            }

    @staticmethod
    async def is_json(input_object):
        """Method to determine whether user input is valid JSON.

        :param input_object: the user's input to check
        :returns: True if valid json object
        """
        try:
            json_object = json.loads(input_object)
            del json_object
            return True
        except ValueError:
            return False

    @staticmethod
    async def parse_response_message(response):
        """Method to determine the message body from a response object. Will return None if message cannot be parsed.

        :param response: the treq response object
        :returns: the response message if parsable, otherwise None
        """
        try:
            return (await response.json())['message']
        except (ValueError, KeyError):
            return None
```

---

### Key Notes:
- All methods that interact with the API are now asynchronous (`async def`) and use `await` for `treq` calls.
- The `requests.Session` logic was removed since `treq` does not use sessions.
- Error handling was adjusted to manually check HTTP status codes, as `treq` does not raise exceptions for HTTP errors.