# Copyright (c) PagerDuty.
# See LICENSE for details.

# Standard libraries
import logging
import sys
import time
from copy import deepcopy
from datetime import datetime
from random import random
from typing import Iterator, Union
from warnings import warn

# Upstream components on which this client is based:
from requests_futures.sessions import FuturesSession
from requests import __version__ as REQUESTS_VERSION

# HTTP client exceptions:
from urllib3.exceptions import HTTPError, PoolError
from requests.exceptions import RequestException

__version__ = '5.4.0'

#######################
### CLIENT DEFAULTS ###
#######################
ITERATION_LIMIT = 1e4
"""
The maximum position of a result in classic pagination.

The offset plus limit parameter may not exceed this number. This is enforced
server-side and is not something the client may override. Rather, this value is
used to short-circuit pagination in order to avoid a HTTP 400 error.

See: `Pagination
<https://developer.pagerduty.com/docs/ZG9jOjExMDI5NTU4-pagination>`_.
"""

TIMEOUT = 60
"""
The default timeout in seconds for any given HTTP request.

Modifying this value will not affect any preexisting API session instances.
Rather, it will only affect new instances. It is recommended to use
:attr:`PDSession.timeout` to configure the timeout for a given session.
"""

TEXT_LEN_LIMIT = 100
"""
The longest permissible length of API content to include in error messages.
"""

# List of canonical API paths
CANONICAL_PATHS = [
    # (List of paths remains unchanged)
]

CURSOR_BASED_PAGINATION_PATHS = [
    # (List of paths remains unchanged)
]

ENTITY_WRAPPER_CONFIG = {
    # (Dictionary remains unchanged)
}

####################
### URL HANDLING ###
####################

def canonical_path(base_url: str, url: str) -> str:
    # (Function remains unchanged)

def endpoint_matches(endpoint_pattern: str, method: str, path: str) -> bool:
    # (Function remains unchanged)

def is_path_param(path_node: str) -> bool:
    # (Function remains unchanged)

def normalize_url(base_url: str, url: str) -> str:
    # (Function remains unchanged)

#######################
### ENTITY WRAPPING ###
#######################

def entity_wrappers(method: str, path: str) -> tuple:
    # (Function remains unchanged)

def infer_entity_wrapper(method: str, path: str) -> str:
    # (Function remains unchanged)

def unwrap(response, wrapper) -> Union[dict, list]:
    # (Function remains unchanged)

###########################
### FUNCTION DECORATORS ###
###########################

def auto_json(method):
    # (Function remains unchanged)

def requires_success(method):
    # (Function remains unchanged)

def resource_url(method):
    # (Function remains unchanged)

def wrapped_entities(method):
    # (Function remains unchanged)

########################
### HELPER FUNCTIONS ###
########################

def deprecated_kwarg(deprecated_name: str, details=None):
    # (Function remains unchanged)

def http_error_message(r, context=None) -> str:
    # (Function remains unchanged)

def last_4(secret: str) -> str:
    # (Function remains unchanged)

def plural_name(obj_type: str) -> str:
    # (Function remains unchanged)

def singular_name(r_name: str) -> str:
    # (Function remains unchanged)

def successful_response(r, context=None) -> Response:
    # (Function remains unchanged)

def truncate_text(text: str) -> str:
    # (Function remains unchanged)

def try_decoding(r) -> Union[dict, list, str]:
    # (Function remains unchanged)

###############
### CLASSES ###
###############

class PDSession(FuturesSession):
    """
    Base class for making HTTP requests to PagerDuty APIs

    This is an opinionated wrapper of `requests_futures.sessions.FuturesSession`_, with a few additional
    features:
    """

    log = None
    max_http_attempts = 10
    max_network_attempts = 3
    parent = None
    permitted_methods = ()
    retry = {}
    sleep_timer = 1.5
    sleep_timer_base = 2
    timeout = TIMEOUT
    url = ""

    def __init__(self, api_key: str, debug=False):
        self.parent = super(PDSession, self)
        self.parent.__init__()
        self.api_key = api_key
        self.log = logging.getLogger(__name__)
        self.print_debug = debug
        self.retry = {}

    def after_set_api_key(self):
        # (Method remains unchanged)

    @property
    def api_key(self) -> str:
        # (Property remains unchanged)

    @api_key.setter
    def api_key(self, api_key):
        # (Setter remains unchanged)

    @property
    def auth_header(self) -> dict:
        # (Property remains unchanged)

    def cooldown_factor(self) -> float:
        # (Method remains unchanged)

    def normalize_params(self, params) -> dict:
        # (Method remains unchanged)

    def normalize_url(self, url) -> str:
        # (Method remains unchanged)

    def postprocess(self, response):
        # (Method remains unchanged)

    def prepare_headers(self, method, user_headers={}) -> dict:
        # (Method remains unchanged)

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
            Custom keyword arguments to pass to ``FuturesSession.request``.
        :type method: str
        :type url: str
        :returns:
            The `requests.Response`_ object corresponding to the HTTP response
        """
        sleep_timer = self.sleep_timer
        network_attempts = 0
        http_attempts = {}
        method = method.strip().upper()
        if method not in self.permitted_methods:
            m_str = ', '.join(self.permitted_methods)
            raise PDClientError(f"Method {method} not supported by this API. " \
                f"Permitted methods: {m_str}")
        req_kw = deepcopy(kwargs)
        full_url = self.normalize_url(url)
        endpoint = "%s %s"%(method.upper(), full_url)

        # Add in any headers specified in keyword arguments:
        headers = kwargs.get('headers', {})
        req_kw.update({
            'headers': self.prepare_headers(method, user_headers=headers),
            'stream': False,
            'timeout': self.timeout
        })

        # Special changes to user-supplied parameters, for convenience
        if 'params' in kwargs and kwargs['params']:
            req_kw['params'] = self.normalize_params(kwargs['params'])

        # Make the request (and repeat w/cooldown if the rate limit is reached):
        while True:
            future = self.parent.request(method, full_url, **req_kw)
            try:
                response = future.result()  # Wait for the response
                self.postprocess(response)
            except (HTTPError, PoolError, RequestException) as e:
                network_attempts += 1
                if network_attempts > self.max_network_attempts:
                    error_msg = f"{endpoint}: Non-transient network " \
                        'error; exceeded maximum number of attempts ' \
                        f"({self.max_network_attempts}) to connect to the API."
                    raise PDClientError(error_msg) from e
                sleep_timer *= self.cooldown_factor()
                self.log.warning(
                    "%s: HTTP or network error: %s. retrying in %g seconds.",
                    endpoint, e.__class__.__name__, sleep_timer)
                time.sleep(sleep_timer)
                continue

            status = response.status_code
            retry_logic = self.retry.get(status, 0)
            if not response.ok and retry_logic != 0:
                # Take special action as defined by the retry logic
                if retry_logic != -1:
                    # Retry a specific number of times (-1 implies infinite)
                    if http_attempts.get(status, 0)>=retry_logic or \
                            sum(http_attempts.values())>self.max_http_attempts:
                        lower_limit = retry_logic
                        if lower_limit > self.max_http_attempts:
                            lower_limit = self.max_http_attempts
                        self.log.error(
                            f"%s: Non-transient HTTP error: exceeded " \
                            'maximum number of attempts (%d) to make a ' \
                            'successful request. Currently encountering ' \
                            'status %d.', endpoint, lower_limit, status)
                        return response
                    http_attempts[status] = 1 + http_attempts.get(status, 0)
                sleep_timer *= self.cooldown_factor()
                self.log.warning("%s: HTTP error (%d); retrying in %g seconds.",
                    endpoint, status, sleep_timer)
                time.sleep(sleep_timer)
                continue
            elif status == 429:
                sleep_timer *= self.cooldown_factor()
                self.log.debug("%s: Hit API rate limit (status 429); " \
                    "retrying in %g seconds", endpoint, sleep_timer)
                time.sleep(sleep_timer)
                continue
            elif status == 401:
                # Stop. Authentication failed. We shouldn't try doing any more,
                # because we'll run into the same problem later anyway.
                raise PDHTTPError(
                    "Received 401 Unauthorized response from the API. The key "
                    "(...%s) may be invalid or deactivated."%self.trunc_key,
                    response)
            else:
                # All went according to plan.
                return response

    @property
    def stagger_cooldown(self) -> float:
        # (Property remains unchanged)

    @stagger_cooldown.setter
    def stagger_cooldown(self, val):
        # (Setter remains unchanged)

    @property
    def trunc_key(self) -> str:
        # (Property remains unchanged)

    @property
    def user_agent(self) -> str:
        # (Property remains unchanged)

class EventsAPISession(PDSession):
    # (Class remains unchanged)

class ChangeEventsAPISession(PDSession):
    # (Class remains unchanged)

class APISession(PDSession):
    # (Class remains unchanged)

class URLError(Exception):
    # (Class remains unchanged)

class PDClientError(Exception):
    # (Class remains unchanged)

class PDHTTPError(PDClientError):
    # (Class remains unchanged)

class PDServerError(PDHTTPError):
    # (Class remains unchanged)
