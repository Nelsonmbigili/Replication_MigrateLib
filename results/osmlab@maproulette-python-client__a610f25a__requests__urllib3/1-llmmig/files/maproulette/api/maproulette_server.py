"""This module contains the basic methods that handle API calls to the MapRoulette API. It uses the urllib3 library to
accomplish this."""

import urllib3
import json
import time
from urllib3.exceptions import HTTPError, MaxRetryError, SSLError
from .errors import HttpError, InvalidJsonError, ConnectionUnavailableError, UnauthorizedError, NotFoundError
from urllib3.filepost import encode_multipart_formdata


class MapRouletteServer:
    """Class that holds the basic requests that can be made to the MapRoulette API."""
    def __init__(self, configuration):
        self.url = configuration.api_url
        self.base_url = configuration.base_url
        self.headers = configuration.headers
        self.certs = configuration.certs
        self.verify = configuration.verify
        self.http = urllib3.PoolManager(
            headers=self.headers,
            cert_reqs='CERT_REQUIRED' if self.verify else 'CERT_NONE',
            cert_file=self.certs if self.certs else None
        )
        if self.__check_health():
            self.session = self.http

    def __check_health(self, retries=3, delay=5):
        """Checks health of connection to host by pinging the URL set in the configuration

        :param retries: the number of retries to use to successfully ping the URL. Default is 3
        :param delay: the number of seconds to wait between retries
        :returns: True if GET request to ping endpoint is successful
        """
        for i in range(retries):
            try:
                response = self.http.request(
                    'GET',
                    self.base_url + '/ping'
                )
                if response.status != 200:
                    print(f"Unsuccessful connection. Retrying in {str(delay)} seconds")
                    time.sleep(delay)
                else:
                    return True
            except (MaxRetryError, SSLError):
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
        response = self.session.request('GET', url)
        return self.__handle_response(response)

    def post(self, endpoint, body=None, params=None):
        """Method that completes a POST request to the MapRoulette API

        :param endpoint: the server endpoint to use for the POST request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        url = self.url + endpoint
        if params:
            url += '?' + urllib3.request.urlencode(params)
        encoded_body = json.dumps(body) if body else None
        response = self.session.request('POST', url, body=encoded_body, headers={'Content-Type': 'application/json'})
        return self.__handle_response(response)

    def put(self, endpoint, body=None, params=None):
        """Method that completes a PUT request to the MapRoulette API

        :param endpoint: the server endpoint to use for the PUT request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        url = self.url + endpoint
        if params:
            url += '?' + urllib3.request.urlencode(params)
        encoded_body = json.dumps(body) if body else None
        response = self.session.request('PUT', url, body=encoded_body, headers={'Content-Type': 'application/json'})
        return self.__handle_response(response)

    def put_file(self, endpoint, body=None, params=None):
        """Method that completes a multipart PUT request to the MapRoulette API

        :param endpoint: the server endpoint to use for the PUT request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        url = self.url + endpoint
        if params:
            url += '?' + urllib3.request.urlencode(params)
        fields, content_type = encode_multipart_formdata(body)
        response = self.session.request('PUT', url, body=fields, headers={'Content-Type': content_type})
        return self.__handle_response(response)

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
        response = self.session.request('DELETE', url)
        return self.__handle_response(response)

    def __handle_response(self, response):
        """Handles the response from the server, raising errors or returning the response data."""
        if response.status >= 400:
            if response.status == 404:
                raise NotFoundError(
                    message=self.parse_response_message(response),
                    status=response.status
                )
            elif response.status == 401:
                raise UnauthorizedError(
                    message=self.parse_response_message(response),
                    status=response.status
                )
            elif response.status == 400:
                raise InvalidJsonError(
                    message=self.parse_response_message(response),
                    status=response.status
                )
            else:
                raise HttpError(
                    message=self.parse_response_message(response),
                    status=response.status
                )
        try:
            return {
                "data": json.loads(response.data.decode('utf-8')),
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
            return json.loads(response.data.decode('utf-8'))['message']
        except (ValueError, KeyError):
            return None
