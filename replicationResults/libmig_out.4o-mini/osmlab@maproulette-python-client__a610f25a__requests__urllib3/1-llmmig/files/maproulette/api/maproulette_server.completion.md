### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, several key changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The `requests` library is a higher-level abstraction over `urllib3`, so we need to handle some functionalities manually.

2. **Session Management**: `requests.Session()` was replaced with `urllib3.PoolManager()`, which is used to manage connections.

3. **Making Requests**: The methods for making HTTP requests (GET, POST, PUT, DELETE) were changed to use `urllib3` methods. The `url` and `params` were combined into a single URL string for the request.

4. **Response Handling**: The response handling was adjusted to work with `urllib3`'s response object, which does not have the same methods as `requests`. For example, `response.json()` was replaced with `json.loads(response.data)`.

5. **Error Handling**: The exceptions raised by `requests` were replaced with appropriate error handling for `urllib3`, which uses different exception classes.

Here is the modified code:

```python
"""This module contains the basic methods that handle API calls to the MapRoulette API. It uses the urllib3 library to
accomplish this."""

import urllib3
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
        self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED' if self.verify else 'CERT_NONE', ca_certs=self.certs)
        if self.__check_health():
            pass  # No session management needed in urllib3

    def __check_health(self, retries=3, delay=5):
        """Checks health of connection to host by pinging the URL set in the configuration

        :param retries: the number of reties to use to successfully ping the URL. Default is 3
        :param delay: the number of seconds to wait between retries
        :returns: True if GET request to ping endpoint is successful
        """
        for i in range(retries):
            try:
                response = self.http.request(
                    'GET',
                    self.base_url + '/ping',
                    headers=self.headers
                )
                if response.status != 200:
                    print(f"Unsuccessful connection. Retrying in {str(delay)} seconds")
                    time.sleep(delay)
                else:
                    return True
            except urllib3.exceptions.NewConnectionError:
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
        url = self.url + endpoint
        if params:
            url += '?' + urllib3.request.urlencode(params)
        response = self.http.request('GET', url, headers=self.headers)
        try:
            if response.status != 200:
                if response.status == 404:
                    raise NotFoundError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
                else:
                    raise HttpError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.TimeoutError) as e:
            raise ConnectionUnavailableError(
                message=self.parse_response_message(response),
                status=response.status
            ) from None
        try:
            return {
                "data": json.loads(response.data),
                "status": response.status
            }
        except ValueError:
            return {
                "data": response.data.decode('utf-8'),
                "status": response.status
            }

    def post(self, endpoint, body=None, params=None):
        """Method that completes a POST request to the MapRoulette API

        :param endpoint: the server endpoint to use for the POST request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        url = self.url + endpoint
        response = self.http.request(
            'POST',
            url,
            headers=self.headers,
            fields=params,
            body=json.dumps(body)
        )
        try:
            if response.status != 200:
                if response.status == 400:
                    raise InvalidJsonError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
                elif response.status == 401:
                    raise UnauthorizedError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
                else:
                    raise HttpError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.TimeoutError) as e:
            raise ConnectionUnavailableError(
                message=self.parse_response_message(response),
                status=response.status
            ) from None
        try:
            return {
                "data": json.loads(response.data),
                "status": response.status
            }
        except ValueError:
            return {
                "data": response.data.decode('utf-8'),
                "status": response.status
            }

    def put(self, endpoint, body=None, params=None):
        """Method that completes a PUT request to the MapRoulette API

        :param endpoint: the server endpoint to use for the PUT request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        url = self.url + endpoint
        response = self.http.request(
            'PUT',
            url,
            headers=self.headers,
            fields=params,
            body=json.dumps(body)
        )
        try:
            if response.status != 200:
                if response.status == 400:
                    raise InvalidJsonError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
                elif response.status == 401:
                    raise UnauthorizedError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
                else:
                    raise HttpError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.TimeoutError) as e:
            raise ConnectionUnavailableError(
                message=self.parse_response_message(response),
                status=response.status
            ) from None
        try:
            return {
                "data": json.loads(response.data),
                "status": response.status
            }
        except ValueError:
            return {
                "data": response.data.decode('utf-8'),
                "status": response.status
            }

    def put_file(self, endpoint, body=None, params=None):
        """Method that completes a multipart PUT request to the MapRoulette API

        :param endpoint: the server endpoint to use for the PUT request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        url = self.url + endpoint
        response = self.http.request(
            'PUT',
            url,
            headers=self.headers,
            fields=params,
            body=body
        )
        try:
            if response.status != 200:
                if response.status == 400:
                    raise InvalidJsonError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
                elif response.status == 401:
                    raise UnauthorizedError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
                else:
                    raise HttpError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.TimeoutError) as e:
            raise ConnectionUnavailableError(
                message=self.parse_response_message(response),
                status=response.status
            ) from None
        try:
            return {
                "data": json.loads(response.data),
                "status": response.status
            }
        except ValueError:
            return {
                "data": response.data.decode('utf-8'),
                "status": response.status
            }

    def delete(self, endpoint, params=None):
        """Method that completes a DELETE request to the MapRoulette API

        :param endpoint: the server endpoint to use for the DELETE request
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        url = self.url + endpoint
        if params:
            url += '?' + urllib3.request.urlencode(params)
        response = self.http.request('DELETE', url, headers=self.headers)
        try:
            if response.status != 200:
                if response.status == 401:
                    raise UnauthorizedError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
                elif response.status == 404:
                    raise NotFoundError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
                else:
                    raise HttpError(
                        message=self.parse_response_message(response),
                        status=response.status
                    ) from None
        except (urllib3.exceptions.NewConnectionError, urllib3.exceptions.TimeoutError) as e:
            raise ConnectionUnavailableError(
                message=self.parse_response_message(response),
                status=response.status
            ) from None
        try:
            return {
                "data": json.loads(response.data),
                "status": response.status
            }
        except ValueError:
            return {
                "data": response.data.decode('utf-8'),
                "status": response.status
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

        :param response: the urllib3 response object
        :returns: the response message if parsable, otherwise None
        """
        try:
            return json.loads(response.data)['message']
        except (ValueError, KeyError):
            return None
```