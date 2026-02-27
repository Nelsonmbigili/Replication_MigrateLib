# Copyright (c) PagerDuty.
# See LICENSE for details.

# Standard libraries
import logging
import sys
import time
import json
from copy import deepcopy
from datetime import datetime
from random import random
from typing import Iterator, Union
from warnings import warn

# HTTP client library
import urllib3
from urllib3.exceptions import HTTPError, MaxRetryError, TimeoutError

__version__ = '5.4.0'

#######################
### CLIENT DEFAULTS ###
#######################
ITERATION_LIMIT = 1e4
TIMEOUT = 60
TEXT_LEN_LIMIT = 100

####################
### URL HANDLING ###
####################

def normalize_url(base_url: str, url: str) -> str:
    """
    Normalize a URL to a complete API URL.

    The ``url`` argument may be a path relative to the base URL or a full URL.

    :param url: The URL to normalize
    :param baseurl:
        The base API URL, excluding any trailing slash, i.e.
        "https://api.pagerduty.com"
    :returns: The full API endpoint URL
    """
    if url.startswith(base_url):
        return url
    elif not (url.startswith('http://') or url.startswith('https://')):
        return base_url.rstrip('/') + "/" + url.lstrip('/')
    else:
        raise URLError(
            f"URL {url} does not start with the API base URL {base_url}"
        )

def try_decoding(response) -> Union[dict, list, str]:
    """
    JSON-decode a response body

    Returns the decoded body if successful; raises an exception otherwise.

    :param response:
        The HTTPResponse object
    """
    try:
        return json.loads(response.data.decode('utf-8'))
    except ValueError as e:
        raise PDServerError(
            "API responded with invalid JSON: " + truncate_text(response.data.decode('utf-8')),
            response,
        )

def truncate_text(text: str) -> str:
    """Truncates a string longer than :attr:`TEXT_LEN_LIMIT`

    :param text: The string to truncate if longer than the limit.
    """
    if len(text) > TEXT_LEN_LIMIT:
        return text[:TEXT_LEN_LIMIT-1]+'...'
    else:
        return text

###############
### CLASSES ###
###############

class PDSession:
    """
    Base class for making HTTP requests to PagerDuty APIs

    This is an opinionated wrapper of `urllib3.PoolManager`, with a few additional
    features:

    - The client will reattempt the request with auto-increasing cooldown/retry
      intervals, with attempt limits configurable through the :attr:`retry`
      attribute.
    - When making requests, headers specified ad-hoc in calls to HTTP verb
      functions will not replace, but will be merged into, default headers.
    - The request URL, if it doesn't already start with the REST API base URL,
      will be prepended with the default REST API base URL.
    - It will only perform requests with methods as given in the
      :attr:`permitted_methods` list, and will raise :class:`PDClientError` for
      any other HTTP methods.

    :param api_key:
        REST API access token to use for HTTP requests
    :param debug:
        Sets :attr:`print_debug`. Set to True to enable verbose command line
        output.
    :type token: str
    :type debug: bool
    """

    def __init__(self, api_key: str, debug=False):
        self.api_key = api_key
        self.log = logging.getLogger(__name__)
        self.print_debug = debug
        self.retry = {}
        self.pool_manager = urllib3.PoolManager()

    def request(self, method, url, **kwargs):
        """
        Make a generic PagerDuty API request.

        :param method:
            The request method to use. Case-insensitive. May be one of get, put,
            post or delete.
        :param url:
            The path/URL to request. If it does not start with the base URL, the
            base URL will be prepended.
        :param **kwargs:
            Custom keyword arguments to pass to ``urllib3.PoolManager.request``.
        :type method: str
        :type url: str
        :returns:
            The `urllib3.response.HTTPResponse` object corresponding to the HTTP response
        """
        full_url = normalize_url(self.url, url)
        headers = kwargs.pop('headers', {})
        headers.update(self.auth_header)

        try:
            response = self.pool_manager.request(
                method.upper(),
                full_url,
                headers=headers,
                timeout=urllib3.Timeout(connect=TIMEOUT, read=TIMEOUT),
                **kwargs
            )
            return response
        except (HTTPError, MaxRetryError, TimeoutError) as e:
            raise PDClientError(f"HTTP request failed: {e}")

    @property
    def auth_header(self) -> dict:
        """
        Generates the header with the API credential used for authentication.
        """
        return {"Authorization": f"Token token={self.api_key}"}

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('DELETE', url, **kwargs)

class PDClientError(Exception):
    """
    General API errors base class.
    """
    pass

class PDServerError(PDClientError):
    """
    Error class representing failed expectations made of the server
    """
    pass
