### Explanation of Changes

To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Session Management**: The `httpx` library uses a different session management approach. The `httpx.Client()` is used to create a session instead of `requests.Session()`.
3. **Exception Handling**: The exceptions raised by `httpx` are different from those in `requests`. Specifically, `httpx` raises `httpx.HTTPStatusError` for HTTP errors and `httpx.ConnectError` for connection issues.
4. **Response Handling**: The response object in `httpx` has similar methods to `requests`, but the exception handling needs to be updated to reflect the new error types.

The following code reflects these changes while maintaining the original structure and style.

### Modified Code

```python
"""This module contains the basic methods that handle API calls to the MapRoulette API. It uses the httpx library to
accomplish this."""

import httpx
import json
import time
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
            self.session = httpx.Client(headers=self.headers, verify=self.verify, cert=self.certs)

    def __check_health(self, retries=3, delay=5):
        """Checks health of connection to host by pinging the URL set in the configuration

        :param retries: the number of reties to use to successfully ping the URL. Default is 3
        :param delay: the number of seconds to wait between retries
        :returns: True if GET request to ping endpoint is successful
        """
        for i in range(retries):
            try:
                response = self.session.get(
                    self.base_url + '/ping',
                    headers=self.headers,
                    verify=self.verify,
                    cert=self.certs
                )
                if not response.is_success:
                    print(f"Unsuccessful connection. Retrying in {str(delay)} seconds")
                    time.sleep(delay)
                else:
                    return True
            except httpx.ConnectError:
                print(f"Connection not available. Attempt {str(i+1)} out of {str(retries)}")
                time.sleep(delay)

        raise ConnectionUnavailableError(
            message='Specified server unavailable'
        )

    def get(self, endpoint, params=None):
        """Method that completes a GET request to the MapRoulette API

        :param endpoint: the server endpoint to use for the GET request
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = self.session.get(
            self.url + endpoint,
            params=params
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
            else:
                raise HttpError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise ConnectionUnavailableError(
                message=self.parse_response_message(e.response),
                status=e.response.status_code
            ) from None
        try:
            return {
                "data": response.json(),
                "status": response.status_code
            }
        except ValueError:
            return {
                "data": response.text,
                "status": response.status_code
            }

    def post(self, endpoint, body=None, params=None):
        """Method that completes a POST request to the MapRoulette API

        :param endpoint: the server endpoint to use for the POST request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = self.session.post(
            self.url + endpoint,
            params=params,
            json=body
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise InvalidJsonError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
            elif e.response.status_code == 401:
                raise UnauthorizedError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
            else:
                raise HttpError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise ConnectionUnavailableError(e) from None
        try:
            return {
                "data": response.json(),
                "status": response.status_code
            }
        except ValueError:
            return {
                "data": response.text,
                "status": response.status_code
            }

    def put(self, endpoint, body=None, params=None):
        """Method that completes a PUT request to the MapRoulette API

        :param endpoint: the server endpoint to use for the PUT request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = self.session.put(
            self.url + endpoint,
            params=params,
            json=body
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise InvalidJsonError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
            elif e.response.status_code == 401:
                raise UnauthorizedError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
            else:
                raise HttpError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise ConnectionUnavailableError(e) from None
        try:
            return {
                "data": response.json(),
                "status": response.status_code
            }
        except ValueError:
            return {
                "data": response.text,
                "status": response.status_code
            }

    def put_file(self, endpoint, body=None, params=None):
        """Method that completes a multipart PUT request to the MapRoulette API

        :param endpoint: the server endpoint to use for the PUT request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = self.session.put(
            self.url + endpoint,
            params=params,
            files=body
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise InvalidJsonError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
            elif e.response.status_code == 401:
                raise UnauthorizedError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
            else:
                raise HttpError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise ConnectionUnavailableError(e) from None
        try:
            return {
                "data": response.json(),
                "status": response.status_code
            }
        except ValueError:
            return {
                "data": response.text,
                "status": response.status_code
            }

    def delete(self, endpoint, params=None):
        """Method that completes a DELETE request to the MapRoulette API

        :param endpoint: the server endpoint to use for the DELETE request
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = self.session.delete(
            self.url + endpoint,
            params=params
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise UnauthorizedError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
            elif e.response.status_code == 404:
                raise NotFoundError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
            else:
                raise HttpError(
                    message=self.parse_response_message(e.response),
                    status=e.response.status_code
                ) from None
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise ConnectionUnavailableError(e) from None
        try:
            return {
                "data": response.json(),
                "status": response.status_code
            }
        except ValueError:
            return {
                "data": response.text,
                "status": response.status_code
            }

    @staticmethod
    def is_json(input_object):
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
    def parse_response_message(response):
        """Method to determine the message body from a response object. Will return None if message cannot be parsed.

        :param response: the HTTPX response object
        :returns: the response message if parsable, otherwise None
        """
        try:
            return json.loads(response.text)['message']
        except (ValueError, KeyError):
            return None
```