### Explanation of Changes

To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `import treq`.
2. **Session Management**: The `requests.Session()` object was removed since `treq` does not require a session object for making requests. Instead, requests can be made directly using `treq`.
3. **Error Handling**: The error handling for HTTP errors was updated to use `treq`'s exceptions. Specifically, `treq` raises `treq.exceptions.HTTPError` instead of `requests.exceptions.HTTPError`.
4. **Response Handling**: The response handling was simplified since `treq` automatically decodes JSON responses. The `response.json()` method is still used, but it is now directly called on the response object returned by `treq`.

### Modified Code

Here is the modified code after migrating to `treq`:

```python
"""This module contains the basic methods that handle API calls to the MapRoulette API. It uses the treq library to
accomplish this."""

import treq
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
            # No session management needed in treq
            pass

    def __check_health(self, retries=3, delay=5):
        """Checks health of connection to host by pinging the URL set in the configuration

        :param retries: the number of reties to use to successfully ping the URL. Default is 3
        :param delay: the number of seconds to wait between retries
        :returns: True if GET request to ping endpoint is successful
        """
        for i in range(retries):
            try:
                response = treq.get(
                    self.base_url + '/ping',
                    headers=self.headers,
                    verify=self.verify,
                    cert=self.certs
                )
                if not response.ok:
                    print(f"Unsuccessful connection. Retrying in {str(delay)} seconds")
                    time.sleep(delay)
                else:
                    return True
            except treq.exceptions.ConnectionError:
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
        response = treq.get(
            self.url + endpoint,
            params=params,
            headers=self.headers,
            verify=self.verify,
            cert=self.certs
        )
        try:
            response.raise_for_status()
        except treq.exceptions.HTTPError as e:
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
        except (treq.exceptions.ConnectionError, treq.exceptions.Timeout) as e:
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
        response = treq.post(
            self.url + endpoint,
            params=params,
            json=body,
            headers=self.headers,
            verify=self.verify,
            cert=self.certs
        )
        try:
            response.raise_for_status()
        except treq.exceptions.HTTPError as e:
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
        except (treq.exceptions.ConnectionError, treq.exceptions.Timeout) as e:
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
        response = treq.put(
            self.url + endpoint,
            params=params,
            json=body,
            headers=self.headers,
            verify=self.verify,
            cert=self.certs
        )
        try:
            response.raise_for_status()
        except treq.exceptions.HTTPError as e:
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
        except (treq.exceptions.ConnectionError, treq.exceptions.Timeout) as e:
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
        response = treq.put(
            self.url + endpoint,
            params=params,
            files=body,
            headers=self.headers,
            verify=self.verify,
            cert=self.certs
        )
        try:
            response.raise_for_status()
        except treq.exceptions.HTTPError as e:
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
        except (treq.exceptions.ConnectionError, treq.exceptions.Timeout) as e:
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
        response = treq.delete(
            self.url + endpoint,
            params=params,
            headers=self.headers,
            verify=self.verify,
            cert=self.certs
        )
        try:
            response.raise_for_status()
        except treq.exceptions.HTTPError as e:
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
        except (treq.exceptions.ConnectionError, treq.exceptions.Timeout) as e:
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

        :param response: the treq response object
        :returns: the response message if parsable, otherwise None
        """
        try:
            return json.loads(response.text)['message']
        except (ValueError, KeyError):
            return None
```