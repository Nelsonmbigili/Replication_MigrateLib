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
from requests_futures.sessions import Response
from requests_futures.sessions import __version__ as REQUESTS_VERSION

# HTTP client exceptions:
from urllib3.exceptions import HTTPError, PoolError
from requests.exceptions import RequestException

__version__ = '5.4.0'

#######################
### CLIENT DEFAULTS ###
#######################
ITERATION_LIMIT = 1e4
TIMEOUT = 60
TEXT_LEN_LIMIT = 100

CANONICAL_PATHS = [
    # (List of canonical paths remains unchanged)
]

CURSOR_BASED_PAGINATION_PATHS = [
    # (List of cursor-based pagination paths remains unchanged)
]

ENTITY_WRAPPER_CONFIG = {
    # (Entity wrapper configuration remains unchanged)
}

####################
### URL HANDLING ###
####################

# (URL handling functions remain unchanged)

#######################
### ENTITY WRAPPING ###
#######################

# (Entity wrapping functions remain unchanged)

###########################
### FUNCTION DECORATORS ###
###########################

# (Function decorators remain unchanged)

########################
### HELPER FUNCTIONS ###
########################

# (Helper functions remain unchanged)

###############
### CLASSES ###
###############

class PDSession(FuturesSession):
    """
    Base class for making HTTP requests to PagerDuty APIs

    This is an opinionated wrapper of `requests_futures.sessions.FuturesSession`,
    with a few additional features:
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
    """

    log = None
    max_http_attempts = 10
    max_network_attempts = 3
    permitted_methods = ()
    retry = {}
    sleep_timer = 1.5
    sleep_timer_base = 2
    timeout = TIMEOUT
    url = ""

    def __init__(self, api_key: str, debug=False):
        super(PDSession, self).__init__()
        self.api_key = api_key
        self.log = logging.getLogger(__name__)
        self.print_debug = debug
        self.retry = {}

    def request(self, method, url, **kwargs) -> Response:
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
        endpoint = "%s %s" % (method.upper(), full_url)

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
            try:
                future = super(PDSession, self).request(method, full_url, **req_kw)
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
                    if http_attempts.get(status, 0) >= retry_logic or \
                            sum(http_attempts.values()) > self.max_http_attempts:
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
                    "(...%s) may be invalid or deactivated." % self.trunc_key,
                    response)
            else:
                # All went according to plan.
                return response

# (Remaining classes and methods remain unchanged)
