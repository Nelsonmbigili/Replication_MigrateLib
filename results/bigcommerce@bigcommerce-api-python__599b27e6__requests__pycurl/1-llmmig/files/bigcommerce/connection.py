"""
Connection Module

Handles put and get operations to the Bigcommerce REST API
"""
import base64
import hashlib
import hmac
import pycurl
from io import BytesIO

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import logging
import jwt

from json import dumps, loads
from math import ceil
from time import sleep

from bigcommerce.exception import *

log = logging.getLogger("bigcommerce.connection")


class Connection(object):
    """
    Connection class manages the connection to the Bigcommerce REST API.
    """

    def __init__(self, host, auth, api_path='/api/v2/{}'):
        self.host = host
        self.api_path = api_path

        self.timeout = 7.0  # need to catch timeout?

        log.info("API Host: %s/%s" % (self.host, self.api_path))

        # Authentication and headers
        self.auth = auth
        self.default_headers = {"Accept": "application/json"}

        self._last_response = None  # for debugging

    def full_path(self, url):
        return "https://" + self.host + self.api_path.format(url)

    def _run_method(self, method, url, data=None, query=None, headers=None):
        if query is None:
            query = {}
        if headers is None:
            headers = {}

        # Make full path if not given
        if url and url[:4] != "http":
            if url[0] == '/':  # can call with /resource if you want
                url = url[1:]
            url = self.full_path(url)
        elif not url:  # blank path
            url = self.full_path(url)

        qs = urlencode(query)
        if qs:
            qs = "?" + qs
        url += qs

        # Prepare headers
        all_headers = self.default_headers.copy()
        all_headers.update(headers)
        header_list = [f"{key}: {value}" for key, value in all_headers.items()]

        # Prepare data
        if data:
            if 'Content-Type' not in all_headers:
                data = dumps(data)
                header_list.append("Content-Type: application/json")
            elif isinstance(data, dict):
                data = urlencode(data)

        # Initialize pycurl
        curl = pycurl.Curl()
        response_buffer = BytesIO()
        header_buffer = BytesIO()

        try:
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
            curl.setopt(pycurl.HEADERFUNCTION, header_buffer.write)
            curl.setopt(pycurl.TIMEOUT, self.timeout)
            curl.setopt(pycurl.HTTPHEADER, header_list)

            # Set HTTP method
            if method == 'GET':
                curl.setopt(pycurl.HTTPGET, True)
            elif method == 'POST':
                curl.setopt(pycurl.POST, True)
                if data:
                    curl.setopt(pycurl.POSTFIELDS, data)
            elif method == 'PUT':
                curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
                if data:
                    curl.setopt(pycurl.POSTFIELDS, data)
            elif method == 'DELETE':
                curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')

            # Set authentication
            if self.auth:
                curl.setopt(pycurl.USERPWD, f"{self.auth[0]}:{self.auth[1]}")

            # Perform the request
            curl.perform()

            # Extract response details
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            response_body = response_buffer.getvalue().decode('utf-8')
            response_headers = header_buffer.getvalue().decode('utf-8')

        except pycurl.error as e:
            raise ConnectionError(f"pycurl error: {e}")
        finally:
            curl.close()

        # Simulate a response object
        response = {
            'status_code': status_code,
            'body': response_body,
            'headers': response_headers
        }
        return response

    # CRUD methods

    def get(self, resource="", rid=None, **query):
        if rid:
            if resource[-1] != '/':
                resource += '/'
            resource += str(rid)
        response = self._run_method('GET', resource, query=query)
        return self._handle_response(resource, response)

    def update(self, resource, rid, updates):
        if resource[-1] != '/':
            resource += '/'
        resource += str(rid)
        return self.put(resource, data=updates)

    def create(self, resource, data):
        return self.post(resource, data)

    def delete(self, resource, rid=None):
        if rid:
            if resource[-1] != '/':
                resource += '/'
            resource += str(rid)
        response = self._run_method('DELETE', resource)
        return self._handle_response(resource, response, suppress_empty=True)

    def make_request(self, method, url, data=None, params=None, headers=None):
        response = self._run_method(method, url, data, params, headers)
        return self._handle_response(url, response)

    def put(self, url, data):
        response = self._run_method('PUT', url, data=data)
        log.debug("OUTPUT: %s" % response['body'])
        return self._handle_response(url, response)

    def post(self, url, data, headers={}):
        response = self._run_method('POST', url, data=data, headers=headers)
        return self._handle_response(url, response)

    def _handle_response(self, url, res, suppress_empty=True):
        self._last_response = res
        result = {}
        status_code = res['status_code']
        body = res['body']

        if status_code in (200, 201, 202):
            try:
                result = loads(body)
            except Exception as e:
                e.message += f" (_handle_response failed to decode JSON: {body})"
                raise
        elif status_code == 204 and not suppress_empty:
            raise EmptyResponseWarning(f"{status_code} @ {url}: {body}", res)
        elif status_code >= 500:
            raise ServerException(f"{status_code} @ {url}: {body}", res)
        elif status_code == 429:
            raise RateLimitingException(f"{status_code} @ {url}: {body}", res)
        elif status_code >= 400:
            raise ClientRequestException(f"{status_code} @ {url}: {body}", res)
        elif status_code >= 300:
            raise RedirectionException(f"{status_code} @ {url}: {body}", res)
        return result

    def __repr__(self):
        return "%s %s%s" % (self.__class__.__name__, self.host, self.api_path)
