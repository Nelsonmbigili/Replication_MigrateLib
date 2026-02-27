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
from httpx import Response, Client
from httpx import __version__ as HTTPX_VERSION

# HTTP client exceptions:
from httpx import HTTPError, RequestError, ConnectError

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

def successful_response(r: Response, context=None) -> Response:
    """Validates the response as successful.

    Returns the response if it was successful; otherwise, raises an exception.

    :param r:
        Response object corresponding to the response received.
    :param context:
        A description of when the HTTP request is happening, for error reporting
    :returns:
        The response object, if it was successful
    """
    if r.is_success:
        return r
    elif r.status_code // 100 == 5:
        raise PDServerError(http_error_message(r, context=context), r)
    elif r.status_code:
        raise PDHTTPError(http_error_message(r, context=context), r)
    else:
        raise PDClientError(http_error_message(r, context=context))

###############
### CLASSES ###
###############

class PDSession:
    """
    Base class for making HTTP requests to PagerDuty APIs

    This is an opinionated wrapper of `httpx.Client`, with a few additional
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

    log = None
    """
    A ``logging.Logger`` object for logging messages. By default it is
    configured without any handlers and so no messages will be emitted. See
    `logger objects
    <https://docs.python.org/3/library/logging.html#logger-objects>`_
    """

    max_http_attempts = 10
    """
    The number of times that the client will retry after error statuses, for any
    that are defined greater than zero in :attr:`retry`.
    """

    max_network_attempts = 3
    """
    The number of times that connecting to the API will be attempted before
    treating the failure as non-transient; a :class:`PDClientError` exception
    will be raised if this happens.
    """

    permitted_methods = ()
    """
    A tuple of the methods permitted by the API which the client implements.

    For instance:

    * The REST API accepts GET, POST, PUT and DELETE.
    * The Events API and Change Events APIs only accept POST.
    """

    retry = {}
    """
    A dict defining the retry behavior for each HTTP response status code.

    Each key in this dictionary is an int representing a HTTP response code. The
    behavior is specified by the int value at each key as follows:

    * ``-1`` to retry without limit.
    * ``0`` has no effect; the default behavior will take effect.
    * ``n``, where ``n > 0``, to retry ``n`` times (or up
      to :attr:`max_http_attempts` total for all statuses, whichever is
      encountered first), and then return the final response.

    The default behavior is to retry without limit on status 429, raise an
    exception on a 401, and return the `httpx.Response` object in any other case
    (assuming a HTTP response was received from the server).
    """

    sleep_timer = 1.5
    """
    Default initial cooldown time factor for rate limiting and network errors.

    Each time that the request makes a followup request, there will be a delay
    in seconds equal to this number times :attr:`sleep_timer_base` to the power
    of how many attempts have already been made so far, unless
    :attr:`stagger_cooldown` is nonzero.
    """

    sleep_timer_base = 2
    """
    After each retry, the time to sleep before reattempting the API connection
    and request will increase by a factor of this amount.
    """

    timeout = TIMEOUT
    """
    This is the value sent to `httpx` as the ``timeout`` parameter that
    determines the TCP read timeout.
    """

    url = ""

    def __init__(self, api_key: str, debug=False):
        self.client = Client()
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
            Custom keyword arguments to pass to ``httpx.Client.request``.
        :type method: str
        :type url: str
        :returns:
            The `httpx.Response` object corresponding to the HTTP response
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
            'timeout': self.timeout
        })

        # Make the request (and repeat w/cooldown if the rate limit is reached):
        while True:
            try:
                response = self.client.request(method, full_url, **req_kw)
                self.postprocess(response)
            except (HTTPError, ConnectError, RequestError) as e:
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
            if not response.is_success and retry_logic != 0:
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
                    "(...%s) may be invalid or deactivated."%self.trunc_key,
                    response)
            else:
                # All went according to plan.
                return response
