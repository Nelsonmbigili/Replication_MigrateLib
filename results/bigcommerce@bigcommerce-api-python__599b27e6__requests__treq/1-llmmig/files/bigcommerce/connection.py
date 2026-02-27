"""
Connection Module

Handles put and get operations to the Bigcommerce REST API
"""
import base64
import hashlib
import hmac

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import logging
import treq
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

        # set up the session
        self.auth = auth
        self.headers = {"Accept": "application/json"}

        self._last_response = None  # for debugging

    def full_path(self, url):
        return "https://" + self.host + self.api_path.format(url)

    async def _run_method(self, method, url, data=None, query=None, headers=None):
        if query is None:
            query = {}
        if headers is None:
            headers = {}

        # make full path if not given
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

        # mess with content
        if data:
            if not headers:  # assume JSON
                data = dumps(data)
                headers = {'Content-Type': 'application/json'}
            if headers and 'Content-Type' not in headers:
                data = dumps(data)
                headers['Content-Type'] = 'application/json'

        headers.update(self.headers)

        log.debug("%s %s" % (method, url))

        # make and send the request
        if method == 'GET':
            response = await treq.get(url, headers=headers, params=query, timeout=self.timeout)
        elif method == 'POST':
            response = await treq.post(url, headers=headers, json=data, timeout=self.timeout)
        elif method == 'PUT':
            response = await treq.put(url, headers=headers, json=data, timeout=self.timeout)
        elif method == 'DELETE':
            response = await treq.delete(url, headers=headers, timeout=self.timeout)
        else:
            raise ValueError("Unsupported HTTP method: %s" % method)

        return response

    # CRUD methods

    async def get(self, resource="", rid=None, **query):
        if rid:
            if resource[-1] != '/':
                resource += '/'
            resource += str(rid)
        response = await self._run_method('GET', resource, query=query)
        return await self._handle_response(resource, response)

    async def update(self, resource, rid, updates):
        if resource[-1] != '/':
            resource += '/'
        resource += str(rid)
        return await self.put(resource, data=updates)

    async def create(self, resource, data):
        return await self.post(resource, data)

    async def delete(self, resource, rid=None):
        if rid:
            if resource[-1] != '/':
                resource += '/'
            resource += str(rid)
        response = await self._run_method('DELETE', resource)
        return await self._handle_response(resource, response, suppress_empty=True)

    async def make_request(self, method, url, data=None, params=None, headers=None):
        response = await self._run_method(method, url, data, params, headers)
        return await self._handle_response(url, response)

    async def put(self, url, data):
        response = await self._run_method('PUT', url, data=data)
        log.debug("OUTPUT: %s" % (await response.text()))
        return await self._handle_response(url, response)

    async def post(self, url, data, headers={}):
        response = await self._run_method('POST', url, data=data, headers=headers)
        return await self._handle_response(url, response)

    async def _handle_response(self, url, res, suppress_empty=True):
        self._last_response = res
        result = {}
        status_code = res.code
        if status_code in (200, 201, 202):
            try:
                result = await res.json()
            except Exception as e:
                e.message += " (_handle_response failed to decode JSON: " + str(await res.text()) + ")"
                raise
        elif status_code == 204 and not suppress_empty:
            raise EmptyResponseWarning("%d %s @ %s: %s" % (status_code, res.phrase, url, await res.text()), res)
        elif status_code >= 500:
            raise ServerException("%d %s @ %s: %s" % (status_code, res.phrase, url, await res.text()), res)
        elif status_code == 429:
            raise RateLimitingException("%d %s @ %s: %s" % (status_code, res.phrase, url, await res.text()), res)
        elif status_code >= 400:
            raise ClientRequestException("%d %s @ %s: %s" % (status_code, res.phrase, url, await res.text()), res)
        elif status_code >= 300:
            raise RedirectionException("%d %s @ %s: %s" % (status_code, res.phrase, url, await res.text()), res)
        return result

    def __repr__(self):
        return "%s %s%s" % (self.__class__.__name__, self.host, self.api_path)
