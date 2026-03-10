"""This module contains the basic methods that handle API calls to the MapRoulette API. It uses the pycurl library to
accomplish this."""

import pycurl
import json
import time
from io import BytesIO
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
            self.session = None  # No session in pycurl

    def __check_health(self, retries=3, delay=5):
        """Checks health of connection to host by pinging the URL set in the configuration

        :param retries: the number of reties to use to successfully ping the URL. Default is 3
        :param delay: the number of seconds to wait between retries
        :returns: True if GET request to ping endpoint is successful
        """
        for i in range(retries):
            try:
                response = self._make_request('GET', self.base_url + '/ping')
                if response['status'] != 200:
                    print(f"Unsuccessful connection. Retrying in {str(delay)} seconds")
                    time.sleep(delay)
                else:
                    return True
            except ConnectionUnavailableError:
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
        response = self._make_request('GET', self.url + endpoint, params=params)
        if response['status'] == 404:
            raise NotFoundError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        elif response['status'] != 200:
            raise HttpError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        return response

    def post(self, endpoint, body=None, params=None):
        """Method that completes a POST request to the MapRoulette API

        :param endpoint: the server endpoint to use for the POST request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = self._make_request('POST', self.url + endpoint, body=body, params=params)
        if response['status'] == 400:
            raise InvalidJsonError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        elif response['status'] == 401:
            raise UnauthorizedError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        elif response['status'] != 200:
            raise HttpError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        return response

    def put(self, endpoint, body=None, params=None):
        """Method that completes a PUT request to the MapRoulette API

        :param endpoint: the server endpoint to use for the PUT request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = self._make_request('PUT', self.url + endpoint, body=body, params=params)
        if response['status'] == 400:
            raise InvalidJsonError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        elif response['status'] == 401:
            raise UnauthorizedError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        elif response['status'] != 200:
            raise HttpError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        return response

    def put_file(self, endpoint, body=None, params=None):
        """Method that completes a multipart PUT request to the MapRoulette API

        :param endpoint: the server endpoint to use for the PUT request
        :param body: the body of the request (optional)
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = self._make_request('PUT', self.url + endpoint, body=body, params=params)
        if response['status'] == 400:
            raise InvalidJsonError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        elif response['status'] == 401:
            raise UnauthorizedError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        elif response['status'] != 200:
            raise HttpError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        return response

    def delete(self, endpoint, params=None):
        """Method that completes a DELETE request to the MapRoulette API

        :param endpoint: the server endpoint to use for the DELETE request
        :param params: the parameters that pertain to the request (optional)
        :returns: a dictionary containing the API response status code as well as the decoded JSON response if decoding
            was successful. If not, the response text is returned.
        """
        response = self._make_request('DELETE', self.url + endpoint, params=params)
        if response['status'] == 401:
            raise UnauthorizedError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        elif response['status'] == 404:
            raise NotFoundError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        elif response['status'] != 200:
            raise HttpError(
                message=self.parse_response_message(response),
                status=response['status']
            )
        return response

    def _make_request(self, method, url, body=None, params=None):
        """Helper method to make HTTP requests using pycurl."""
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in self.headers.items()])
        c.setopt(c.SSL_VERIFYPEER, self.verify)
        if self.certs:
            c.setopt(c.CAINFO, self.certs)

        if method == 'POST':
            c.setopt(c.POST, 1)
            if body:
                c.setopt(c.POSTFIELDS, json.dumps(body))
                c.setopt(c.HTTPHEADER, [f"Content-Type: application/json"] + [f"{key}: {value}" for key, value in self.headers.items()])
        elif method == 'PUT':
            c.setopt(c.CUSTOMREQUEST, 'PUT')
            if body:
                c.setopt(c.POSTFIELDS, json.dumps(body))
                c.setopt(c.HTTPHEADER, [f"Content-Type: application/json"] + [f"{key}: {value}" for key, value in self.headers.items()])
        elif method == 'DELETE':
            c.setopt(c.CUSTOMREQUEST, 'DELETE')
            if params:
                url += '?' + '&'.join([f"{key}={value}" for key, value in params.items()])
                c.setopt(c.URL, url)

        c.perform()
        status_code = c.getinfo(c.RESPONSE_CODE)
        response_data = buffer.getvalue().decode('utf-8')
        c.close()

        return {
            "data": json.loads(response_data) if self.is_json(response_data) else response_data,
            "status": status_code
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

        :param response: the response dictionary
        :returns: the response message if parsable, otherwise None
        """
        try:
            return response['data']['message']
        except (ValueError, KeyError):
            return None
