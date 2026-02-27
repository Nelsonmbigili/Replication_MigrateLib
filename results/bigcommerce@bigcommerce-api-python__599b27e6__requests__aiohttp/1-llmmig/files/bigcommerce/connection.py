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
import aiohttp
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

        self.timeout = aiohttp.ClientTimeout(total=7.0)  # need to catch timeout?

        log.info("API Host: %s/%s" % (self.host, self.api_path))

        # set up the session
        self._session = None
        self.auth = auth
        self.headers = {"Accept": "application/json"}

        self._last_response = None  # for debugging

    async def _initialize_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(auth=self.auth, headers=self.headers, timeout=self.timeout)

    def full_path(self, url):
        return "https://" + self.host + self.api_path.format(url)

    async def _run_method(self, method, url, data=None, query=None, headers=None):
        await self._initialize_session()

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

        log.debug("%s %s" % (method, url))

        # make and send the request
        async with self._session.request(method, url, data=data, headers=headers) as response:
            return await self._handle_response(url, response)

    # CRUD methods

    async def get(self, resource="", rid=None, **query):
        if rid:
            if resource[-1] != '/':
                resource += '/'
            resource += str(rid)
        return await self._run_method('GET', resource, query=query)

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
        return await self._run_method('DELETE', resource)

    # Raw-er stuff

    async def make_request(self, method, url, data=None, params=None, headers=None):
        return await self._run_method(method, url, data, params, headers)

    async def put(self, url, data):
        response = await self._run_method('PUT', url, data=data)
        log.debug("OUTPUT: %s" % response)
        return response

    async def post(self, url, data, headers={}):
        return await self._run_method('POST', url, data=data, headers=headers)

    async def _handle_response(self, url, res, suppress_empty=True):
        self._last_response = res
        result = {}
        if res.status in (200, 201, 202):
            try:
                result = await res.json()
            except Exception as e:
                e.message += " (_handle_response failed to decode JSON: " + await res.text() + ")"
                raise
        elif res.status == 204 and not suppress_empty:
            raise EmptyResponseWarning("%d %s @ %s: %s" % (res.status, res.reason, url, await res.text()), res)
        elif res.status >= 500:
            raise ServerException("%d %s @ %s: %s" % (res.status, res.reason, url, await res.text()), res)
        elif res.status == 429:
            raise RateLimitingException("%d %s @ %s: %s" % (res.status, res.reason, url, await res.text()), res)
        elif res.status >= 400:
            raise ClientRequestException("%d %s @ %s: %s" % (res.status, res.reason, url, await res.text()), res)
        elif res.status >= 300:
            raise RedirectionException("%d %s @ %s: %s" % (res.status, res.reason, url, await res.text()), res)
        return result

    async def close(self):
        if self._session:
            await self._session.close()

    def __repr__(self):
        return "%s %s%s" % (self.__class__.__name__, self.host, self.api_path)


# Similar changes would be applied to OAuthConnection and GraphQLConnection classes.
