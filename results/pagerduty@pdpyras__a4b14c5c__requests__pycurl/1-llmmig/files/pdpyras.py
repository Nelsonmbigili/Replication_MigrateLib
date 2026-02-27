# Copyright (c) PagerDuty.
# See LICENSE for details.

# Standard libraries
import logging
import sys
import time
import json
from io import BytesIO
from copy import deepcopy
from datetime import datetime
from random import random
from typing import Iterator, Union
from warnings import warn

# HTTP client library
import pycurl

__version__ = '5.4.0'

#######################
### CLIENT DEFAULTS ###
#######################
ITERATION_LIMIT = 1e4
TIMEOUT = 60
TEXT_LEN_LIMIT = 100

########################
### HELPER FUNCTIONS ###
########################

def truncate_text(text: str) -> str:
    """Truncates a string longer than TEXT_LEN_LIMIT."""
    if len(text) > TEXT_LEN_LIMIT:
        return text[:TEXT_LEN_LIMIT - 1] + '...'
    else:
        return text

def try_decoding(response_body: bytes) -> Union[dict, list, str]:
    """JSON-decode a response body."""
    try:
        return json.loads(response_body.decode('utf-8'))
    except ValueError as e:
        raise PDServerError("API responded with invalid JSON: " + truncate_text(response_body.decode('utf-8')))

#######################
### CUSTOM EXCEPTIONS ###
#######################

class PDClientError(Exception):
    """General API errors base class."""
    pass

class PDHTTPError(PDClientError):
    """Error class representing HTTP errors."""
    pass

class PDServerError(PDHTTPError):
    """Error class representing server-side errors."""
    pass

#######################
### PYCURL SESSION ###
#######################

class PyCurlSession:
    """
    A custom session class using pycurl for HTTP requests.
    """

    def __init__(self, base_url: str, timeout: int = TIMEOUT):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.headers = {}
        self.log = logging.getLogger(__name__)

    def request(self, method: str, url: str, headers: dict = None, data: dict = None, params: dict = None) -> dict:
        """
        Perform an HTTP request using pycurl.
        """
        full_url = self._build_url(url, params)
        buffer = BytesIO()
        curl = pycurl.Curl()

        try:
            # Set URL and method
            curl.setopt(pycurl.URL, full_url.encode('utf-8'))
            curl.setopt(pycurl.CUSTOMREQUEST, method.upper())

            # Set headers
            final_headers = self._prepare_headers(headers)
            curl.setopt(pycurl.HTTPHEADER, [f"{k}: {v}" for k, v in final_headers.items()])

            # Set data for POST/PUT
            if method.upper() in ['POST', 'PUT'] and data:
                curl.setopt(pycurl.POSTFIELDS, json.dumps(data))

            # Set timeout
            curl.setopt(pycurl.TIMEOUT, self.timeout)

            # Write response to buffer
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

            # Perform the request
            curl.perform()

            # Get HTTP response code
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)

            # Parse response
            response_body = buffer.getvalue()
            response_data = try_decoding(response_body)

            # Handle HTTP errors
            if status_code >= 400:
                raise PDHTTPError(f"HTTP error {status_code}: {response_body.decode('utf-8')}")

            return response_data

        except pycurl.error as e:
            raise PDClientError(f"Network error: {e}")

        finally:
            curl.close()
            buffer.close()

    def _build_url(self, url: str, params: dict = None) -> str:
        """
        Build the full URL with query parameters.
        """
        if not url.startswith('http'):
            url = f"{self.base_url}/{url.lstrip('/')}"
        if params:
            query_string = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query_string}"
        return url

    def _prepare_headers(self, user_headers: dict = None) -> dict:
        """
        Prepare headers for the request.
        """
        headers = deepcopy(self.headers)
        if user_headers:
            headers.update(user_headers)
        return headers

#######################
### PAGERDUTY CLIENT ###
#######################

class PDSession(PyCurlSession):
    """
    Base class for making HTTP requests to PagerDuty APIs using pycurl.
    """

    def __init__(self, api_key: str, base_url: str = "https://api.pagerduty.com", timeout: int = TIMEOUT):
        super().__init__(base_url, timeout)
        self.api_key = api_key
        self.headers.update({
            'Authorization': f"Token token={self.api_key}",
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Content-Type': 'application/json',
        })

    def get(self, url: str, params: dict = None) -> dict:
        """
        Perform a GET request.
        """
        return self.request('GET', url, params=params)

    def post(self, url: str, data: dict = None) -> dict:
        """
        Perform a POST request.
        """
        return self.request('POST', url, data=data)

    def put(self, url: str, data: dict = None) -> dict:
        """
        Perform a PUT request.
        """
        return self.request('PUT', url, data=data)

    def delete(self, url: str) -> dict:
        """
        Perform a DELETE request.
        """
        return self.request('DELETE', url)
