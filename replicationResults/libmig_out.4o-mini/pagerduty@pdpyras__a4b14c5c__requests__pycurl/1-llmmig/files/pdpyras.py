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
import pycurl
from io import BytesIO

__version__ = '5.4.0'

#######################
### CLIENT DEFAULTS ###
#######################
ITERATION_LIMIT = 1e4
TIMEOUT = 60
TEXT_LEN_LIMIT = 100

# List of canonical API paths
CANONICAL_PATHS = [
    # (same as original)
]

CURSOR_BASED_PAGINATION_PATHS = [
    # (same as original)
]

ENTITY_WRAPPER_CONFIG = {
    # (same as original)
}

####################
### URL HANDLING ###
####################

def canonical_path(base_url: str, url: str) -> str:
    # (same as original)

def endpoint_matches(endpoint_pattern: str, method: str, path: str) -> bool:
    # (same as original)

def is_path_param(path_node: str) -> bool:
    # (same as original)

def normalize_url(base_url: str, url: str) -> str:
    # (same as original)

#######################
### ENTITY WRAPPING ###
#######################

def entity_wrappers(method: str, path: str) -> tuple:
    # (same as original)

def unwrap(response_body: str, wrapper) -> Union[dict, list]:
    # (same as original)

###########################
### FUNCTION DECORATORS ###
###########################

def auto_json(method):
    # (same as original)

def requires_success(method):
    # (same as original)

def resource_url(method):
    # (same as original)

def wrapped_entities(method):
    # (same as original)

########################
### HELPER FUNCTIONS ###
########################

def deprecated_kwarg(deprecated_name: str, details=None):
    # (same as original)

def http_error_message(status_code: int, context=None) -> str:
    # (same as original)

def last_4(secret: str) -> str:
    # (same as original)

def plural_name(obj_type: str) -> str:
    # (same as original)

def singular_name(r_name: str) -> str:
    # (same as original)

def successful_response(response_body: str, status_code: int, context=None) -> str:
    """Validates the response as successful."""
    if status_code == 200:
        return response_body
    else:
        raise PDHTTPError(http_error_message(status_code, context))

def truncate_text(text: str) -> str:
    # (same as original)

def try_decoding(response_body: str) -> Union[dict, list, str]:
    """JSON-decode a response body."""
    try:
        return json.loads(response_body)
    except ValueError as e:
        raise PDServerError(
            "API responded with invalid JSON: " + truncate_text(response_body),
        )

###############
### CLASSES ###
###############

class PDSession:
    """
    Base class for making HTTP requests to PagerDuty APIs
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
        self.api_key = api_key
        self.log = logging.getLogger(__name__)
        self.print_debug = debug
        self.retry = {}

    def request(self, method, url, **kwargs) -> str:
        """Make a generic PagerDuty API request."""
        sleep_timer = self.sleep_timer
        network_attempts = 0
        method = method.strip().upper()
        if method not in self.permitted_methods:
            m_str = ', '.join(self.permitted_methods)
            raise PDClientError(f"Method {method} not supported by this API. " \
                f"Permitted methods: {m_str}")

        full_url = normalize_url(self.url, url)
        endpoint = "%s %s" % (method.upper(), full_url)

        # Prepare headers
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Token token={self.api_key}'
        headers['User-Agent'] = self.user_agent

        # Make the request using pycurl
        response_buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, full_url)
        c.setopt(c.WRITEFUNCTION, response_buffer.write)
        c.setopt(c.TIMEOUT, self.timeout)
        c.setopt(c.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()])

        while True:
            try:
                c.perform()
                response_code = c.getinfo(c.RESPONSE_CODE)
                response_body = response_buffer.getvalue().decode('utf-8')
                successful_response(response_body, response_code)
                return response_body
            except pycurl.error as e:
                network_attempts += 1
                if network_attempts > self.max_network_attempts:
                    raise PDClientError(f"{endpoint}: Non-transient network error; exceeded maximum number of attempts.") from e
                sleep_timer *= self.cooldown_factor()
                self.log.warning("%s: HTTP or network error: %s. retrying in %g seconds.", endpoint, e, sleep_timer)
                time.sleep(sleep_timer)
                continue
            finally:
                c.close()

    @property
    def user_agent(self) -> str:
        return 'pdpyras/%s python-pycurl/%s Python/%d.%d' % (
            __version__,
            pycurl.version,
            sys.version_info.major,
            sys.version_info.minor
        )

# (Other classes like EventsAPISession, ChangeEventsAPISession, APISession would follow the same pattern)
