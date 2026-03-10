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
import treq
from treq import __version__ as TREQ_VERSION

# HTTP client exceptions:
from urllib3.exceptions import HTTPError, PoolError

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

def unwrap(response, wrapper) -> Union[dict, list]:
    body = try_decoding(response)
    endpoint = "%s %s"%(response.request.method.upper(), response.request.url)
    if wrapper is not None:
        bod_type = type(body)
        error_msg = f"Expected response body from {endpoint} after JSON-" \
            f"decoding to be a dictionary with a key \"{wrapper}\", but "
        if bod_type is dict:
            if wrapper in body:
                return body[wrapper]
            else:
                keys = truncate_text(', '.join(body.keys()))
                raise PDServerError(
                    error_msg + f"its keys are: {keys}",
                    response
                )
        else:
            raise PDServerError(
                error_msg + f"its type is {bod_type}.",
                response
            )
    else:
        return body

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

def http_error_message(r, context=None) -> str:
    # (same as original)

def last_4(secret: str) -> str:
    # (same as original)

def plural_name(obj_type: str) -> str:
    # (same as original)

def singular_name(r_name: str) -> str:
    # (same as original)

def successful_response(r, context=None):
    """Validates the response as successful."""
    if r.status_code == 200:
        return r
    elif r.status_code / 100 == 5:
        raise PDServerError(http_error_message(r, context=context), r)
    elif bool(r.status_code):
        raise PDHTTPError(http_error_message(r, context=context), r)
    else:
        raise PDClientError(http_error_message(r, context=context))

def truncate_text(text: str) -> str:
    # (same as original)

def try_decoding(r) -> Union[dict, list, str]:
    """
    JSON-decode a response body
    """
    try:
        return r.json()
    except ValueError as e:
        raise PDServerError(
            "API responded with invalid JSON: " + truncate_text(r.text),
            r,
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

    def after_set_api_key(self):
        pass

    @property
    def auth_header(self) -> dict:
        raise NotImplementedError

    def cooldown_factor(self) -> float:
        return self.sleep_timer_base*(1+self.stagger_cooldown*random())

    def normalize_params(self, params) -> dict:
        # (same as original)

    def postprocess(self, response):
        # (same as original)

    def prepare_headers(self, method, user_headers={}) -> dict:
        # (same as original)

    def request(self, method, url, **kwargs):
        """
        Make a generic PagerDuty API request.
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

        # Special changes to user-supplied parameters, for convenience
        if 'params' in kwargs and kwargs['params']:
            req_kw['params'] = self.normalize_params(kwargs['params'])

        while True:
            try:
                response = treq.request(method, full_url, **req_kw)
                self.postprocess(response)
            except (HTTPError, PoolError) as e:
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
                if retry_logic != -1:
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
                raise PDHTTPError(
                    "Received 401 Unauthorized response from the API. The key "
                    "(...%s) may be invalid or deactivated."%self.trunc_key,
                    response)
            else:
                return response

    @property
    def trunc_key(self) -> str:
        return last_4(self.api_key)

class EventsAPISession(PDSession):
    """
    Session class for submitting events to the PagerDuty v2 Events API.
    """

    permitted_methods = ('POST',)
    url = "https://events.pagerduty.com"

    def __init__(self, api_key: str, debug=False):
        super(EventsAPISession, self).__init__(api_key, debug)
        self.retry[500] = 2
        self.retry[502] = 4
        self.retry[503] = 6
        self.retry[504] = 6

    @property
    def auth_header(self) -> dict:
        return {}

    def acknowledge(self, dedup_key) -> str:
        return self.send_event('acknowledge', dedup_key=dedup_key)

    def prepare_headers(self, method, user_headers={}) -> dict:
        headers = {}
        headers.update(self.headers)
        headers.update({
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent,
        })
        headers.update(user_headers)
        return headers

    def resolve(self, dedup_key) -> str:
        return self.send_event('resolve', dedup_key=dedup_key)

    def send_event(self, action, dedup_key=None, **properties) -> str:
        actions = ('trigger', 'acknowledge', 'resolve')
        if action not in actions:
            raise ValueError("Event action must be one of: "+', '.join(actions))

        event = {'event_action': action}
        event.update(properties)
        if isinstance(dedup_key, str):
            event['dedup_key'] = dedup_key
        elif not action == 'trigger':
            raise ValueError("The dedup_key property is required for"
                "event_action=%s events, and it must be a string." % action)
        response = successful_response(
            self.post('/v2/enqueue', json=event),
            context='submitting an event to the events API',
        )
        response_body = try_decoding(response)
        if type(response_body) is not dict or 'dedup_key' not in response_body:
            err_msg = 'Malformed response body from the events API; it is ' \
                'not a dict that has a key named "dedup_key" after ' \
                'decoding. Body = ' + truncate_text(response.text)
            raise PDServerError(err_msg, response)
        return response_body['dedup_key']

    def post(self, *args, **kw) -> Response:
        if 'json' in kw and hasattr(kw['json'], 'update'):
            kw['json'].update({'routing_key': self.api_key})
        return super(EventsAPISession, self).post(*args, **kw)

    def trigger(self, summary, source, dedup_key=None, severity='critical',
                payload=None, custom_details=None, images=None, links=None) -> str:
        for local in ('payload', 'custom_details'):
            local_var = locals()[local]
            if not (local_var is None or type(local_var) is dict):
                raise ValueError(local + " must be a dict")
        event = {'payload': {'summary': summary, 'source': source,
                             'severity': severity}}
        if type(payload) is dict:
            event['payload'].update(payload)
        if type(custom_details) is dict:
            details = event.setdefault('payload', {}).get('custom_details', {})
            details.update(custom_details)
            event['payload']['custom_details'] = details
        if images:
            event['images'] = images
        if links:
            event['links'] = links
        return self.send_event('trigger', dedup_key=dedup_key, **event)

class ChangeEventsAPISession(PDSession):
    """
    Session class for submitting events to the PagerDuty v2 Change Events API.
    """

    permitted_methods = ('POST',)
    url = "https://events.pagerduty.com"

    def __init__(self, api_key: str, debug=False):
        super(ChangeEventsAPISession, self).__init__(api_key, debug)
        self.retry[500] = 2
        self.retry[502] = 4
        self.retry[503] = 6

    @property
    def auth_header(self) -> dict:
        return {}

    @property
    def event_timestamp(self) -> str:
        return datetime.utcnow().isoformat() + 'Z'

    def prepare_headers(self, method, user_headers={}) -> dict:
        headers = deepcopy(self.headers)
        headers.update({
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent,
        })
        if user_headers:
            headers.update(user_headers)
        return headers

    def send_change_event(self, **properties):
        event = deepcopy(properties)
        response = self.post('/v2/change/enqueue', json=event)
        response_body = try_decoding(successful_response(
            response,
            context="submitting change event",
        ))
        return response_body.get("id", None)

    def submit(self, summary, source=None, custom_details=None, links=None,
               timestamp=None) -> str:
        local_var = locals()['custom_details']
        if not (local_var is None or isinstance(local_var, dict)):
            raise ValueError("custom_details must be a dict")
        if timestamp is None:
            timestamp = self.event_timestamp
        event = {
            'routing_key': self.api_key,
            'payload': {
                'summary': summary,
                'timestamp': timestamp,
            }
        }
        if isinstance(source, str):
            event['payload']['source'] = source
        if isinstance(custom_details, dict):
            event['payload']['custom_details'] = custom_details
        if links:
            event['links'] = links
        return self.send_change_event(**event)

class APISession(PDSession):
    """
    PagerDuty REST API v2 session object class.
    """

    api_call_counts = None
    api_time = None
    default_from = None
    default_page_size = 100
    permitted_methods = ('GET', 'POST', 'PUT', 'DELETE')
    url = 'https://api.pagerduty.com'

    def __init__(self, api_key: str, default_from=None,
                 auth_type='token', debug=False):
        self.api_call_counts = {}
        self.api_time = {}
        self.auth_type = auth_type
        super(APISession, self).__init__(api_key, debug=debug)
        self.default_from = default_from
        self.headers.update({
            'Accept': 'application/vnd.pagerduty+json;version=2',
        })

    def after_set_api_key(self):
        self._subdomain = None

    @property
    def api_key_access(self) -> str:
        if not hasattr(self, '_api_key_access') or self._api_key_access is None:
            response = self.get('/users/me')
            if response.status_code == 400:
                message = try_decoding(response).get('error', '')
                if 'account-level access token' in message:
                    self._api_key_access = 'account'
                else:
                    self._api_key_access = None
                    self.log.error("Failed to obtain API key access level; "
                                   "the API did not respond as expected.")
                    self.log.debug("Body = %s", truncate_text(response.text))
            else:
                self._api_key_access = 'user'
        return self._api_key_access

    @property
    def auth_type(self) -> str:
        return self._auth_type

    @auth_type.setter
    def auth_type(self, value: str):
        if value not in ('token', 'bearer', 'oauth2'):
            raise AttributeError("auth_type value must be \"token\" (default) "
                                 "or \"bearer\" or \"oauth\" to use OAuth2 authentication.")
        self._auth_type = value

    @property
    def auth_header(self) -> dict:
        if self.auth_type in ('bearer', 'oauth2'):
            return {"Authorization": "Bearer " + self.api_key}
        else:
            return {"Authorization": "Token token=" + self.api_key}

    def dict_all(self, path: str, **kw) -> dict:
        by = kw.pop('by', 'id')
        iterator = self.iter_all(path, **kw)
        return {obj[by]: obj for obj in iterator}

    def find(self, resource, query, attribute='name', params=None) \
            -> Union[dict, None]:
        query_params = {}
        if params is not None:
            query_params.update(params)
        query_params.update({'query': query})
        simplify = lambda s: str(s).lower()
        search_term = simplify(query)
        equiv = lambda s: simplify(s[attribute]) == search_term
        obj_iter = self.iter_all(resource, params=query_params)
        return next(iter(filter(equiv, obj_iter)), None)

    def iter_all(self, url, params=None, page_size=None, item_hook=None,
                  total=False) -> Iterator[dict]:
        path = canonical_path(self.url, url)
        endpoint = f"GET {path}"

        if path in CURSOR_BASED_PAGINATION_PATHS:
            return self.iter_cursor(url, params=params)

        nodes = path.split('/')
        if is_path_param(nodes[-1]):
            raise URLError(f"Path {path} (URL={url}) is formatted like an " \
                            "individual resource versus a resource collection. It is " \
                            "therefore assumed to not support pagination.")
        _, wrapper = entity_wrappers('GET', path)

        if wrapper is None:
            raise URLError(f"Pagination is not supported for {endpoint}.")

        data = {}
        if page_size is None:
            data['limit'] = self.default_page_size
        else:
            data['limit'] = page_size
        if total:
            data['total'] = 1
        if isinstance(params, (dict, list)):
            data.update(dict(params))

        more = True
        offset = 0
        if params is not None:
            offset = int(params.get('offset', 0))
        n = 0
        while more:
            data['offset'] = offset
            highest_record_index = int(data['offset']) + int(data['limit'])
            if highest_record_index > ITERATION_LIMIT:
                iter_limit = '%d' % ITERATION_LIMIT
                warn(
                    f"Stopping iter_all on {endpoint} at " \
                    f"limit+offset={highest_record_index} " \
                    'as this exceeds the maximum permitted by the API ' \
                    f"({iter_limit}). The set of results may be incomplete."
                )
                return

            r = successful_response(
                self.get(url, params=data.copy()),
                context='classic pagination'
            )
            body = try_decoding(r)
            results = unwrap(r, wrapper)

            data['limit'] = len(results)
            offset += data['limit']
            more = False
            total_count = '?'
            if 'more' in body:
                more = body['more']
            else:
                warn(
                    f"Endpoint GET {path} responded with no \"more\" property" \
                    ' in the response, so pagination is not supported ' \
                    '(or this is an API bug). Only results from the first ' \
                    'request will be yielded. You can use rget with this ' \
                    'endpoint instead to avoid this warning.'
                )
            if 'total' in body:
                total_count = body['total']

            for result in results:
                n += 1
                if hasattr(item_hook, '__call__'):
                    item_hook(result, n, total_count)
                yield result

    def iter_cursor(self, url, params=None, item_hook=None) -> Iterator[dict]:
        path = canonical_path(self.url, url)
        if path not in CURSOR_BASED_PAGINATION_PATHS:
            raise URLError(f"{path} does not support cursor-based pagination.")
        _, wrapper = entity_wrappers('GET', path)
        user_params = {}
        if isinstance(params, (dict, list)):
            user_params.update(dict(params))

        more = True
        next_cursor = None
        total = 0

        while more:
            if next_cursor:
                user_params.update({'cursor': next_cursor})
            r = successful_response(
                self.get(url, params=user_params),
                context='cursor-based pagination',
            )

            body = try_decoding(r)
            results = unwrap(r, wrapper)
            for result in results:
                total += 1
                if hasattr(item_hook, '__call__'):
                    item_hook(result, total, '?')
                yield result
            next_cursor = body.get('next_cursor', None)
            more = bool(next_cursor)

    @resource_url
    @auto_json
    def jget(self, url, **kw) -> Union[dict, list]:
        return self.get(url, **kw)

    @resource_url
    @auto_json
    def jpost(self, url, **kw) -> Union[dict, list]:
        return self.post(url, **kw)

    @resource_url
    @auto_json
    def jput(self, url, **kw) -> Union[dict, list]:
        return self.put(url, **kw)

    def list_all(self, url, **kw) -> list:
        return list(self.iter_all(url, **kw))

    def persist(self, resource, attr, values, update=False):
        if attr not in values:
            raise ValueError("Argument `values` must contain a key equal "
                             "to the `attr` argument (expected idempotency key: '%s')." % attr)
        existing = self.find(resource, values[attr], attribute=attr)
        if existing:
            if update:
                original = {}
                original.update(existing)
                existing.update(values)
                if original != existing:
                    existing = self.rput(existing, json=existing)
            return existing
        else:
            return self.rpost(resource, json=values)

    def postprocess(self, response, suffix=None):
        method = response.request.method.upper()
        url = response.request.url
        status = response.status_code
        request_date = response.headers.get('date', '(missing header)')
        request_id = response.headers.get('x-request-id', '(missing header)')
        request_time = response.elapsed.total_seconds()

        try:
            endpoint = "%s %s" % (method, canonical_path(self.url, url))
        except URLError:
            endpoint = "%s %s" % (method, url)
        self.api_call_counts.setdefault(endpoint, 0)
        self.api_time.setdefault(endpoint, 0.0)
        self.api_call_counts[endpoint] += 1
        self.api_time[endpoint] += request_time

        self.log.debug("Request completed: #method=%s|#url=%s|#status=%d|"
                       "#x_request_id=%s|#date=%s|#wall_time_s=%g", method, url, status,
                       request_id, request_date, request_time)
        if int(status / 100) == 5:
            self.log.error("PagerDuty API server error (%d)! "
                           "For additional diagnostics, contact PagerDuty support "
                           "and reference x_request_id=%s / date=%s",
                           status, request_id, request_date)

    def prepare_headers(self, method, user_headers={}) -> dict:
        headers = deepcopy(self.headers)
        headers['User-Agent'] = self.user_agent
        if self.default_from is not None:
            headers['From'] = self.default_from
        if method in ('POST', 'PUT'):
            headers['Content-Type'] = 'application/json'
        if user_headers:
            headers.update(user_headers)
        return headers

    @resource_url
    @requires_success
    def rdelete(self, resource, **kw) -> Response:
        return self.delete(resource, **kw)

    @resource_url
    @wrapped_entities
    def rget(self, resource, **kw) -> Union[dict, list]:
        return self.get(resource, **kw)

    @wrapped_entities
    def rpost(self, path, **kw) -> Union[dict, list]:
        return self.post(path, **kw)

    @resource_url
    @wrapped_entities
    def rput(self, resource, **kw) -> Union[dict, list]:
        return self.put(resource, **kw)

    @property
    def subdomain(self) -> str:
        if not hasattr(self, '_subdomain') or self._subdomain is None:
            try:
                url = self.rget('users', params={'limit': 1})[0]['html_url']
                self._subdomain = url.split('/')[2].split('.')[0]
            except PDClientError as e:
                self.log.error("Failed to obtain subdomain; encountered error.")
                self._subdomain = None
                raise e
        return self._subdomain

    @property
    def total_call_count(self) -> int:
        return sum(self.api_call_counts.values())

    @property
    def total_call_time(self) -> float:
        return sum(self.api_time.values())

    @property
    def trunc_token(self) -> str:
        return last_4(self.api_key)

class URLError(Exception):
    pass

class PDClientError(Exception):
    response = None

    def __init__(self, message, response=None):
        self.msg = message
        self.response = response
        super(PDClientError, self).__init__(message)

class PDHTTPError(PDClientError):
    def __init__(self, message, response):
        super(PDHTTPError, self).__init__(message, response=response)

class PDServerError(PDHTTPError):
    pass
