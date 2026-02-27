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


class OAuthConnection(Connection):
    """
    Class for making OAuth requests on the Bigcommerce v2 API

    Providing a value for access_token allows immediate access to resources within registered scope.
    Otherwise, you may use fetch_token with the code, context, and scope passed to your application's callback url
    to retrieve an access token.

    The verify_payload method is also provided for authenticating signed payloads passed to an application's load url.
    """

    def __init__(self, client_id, store_hash, access_token=None, host='api.bigcommerce.com',
                 api_path='/stores/{}/v2/{}', rate_limiting_management=None):
        self.client_id = client_id
        self.store_hash = store_hash
        self.host = host
        self.api_path = api_path
        self.timeout = 7.0  # can attach to session?
        self.rate_limiting_management = rate_limiting_management

        self.access_token = access_token
        self.headers = {"Accept": "application/json"}

        self._last_response = None  # for debugging

        self.rate_limit = {}

    def full_path(self, url):
        return "https://" + self.host + self.api_path.format(self.store_hash, url)

    @staticmethod
    def _oauth_headers(cid, atoken):
        return {'X-Auth-Client': cid,
                'X-Auth-Token': atoken}

    @staticmethod
    def verify_payload(signed_payload, client_secret):
        """
        Given a signed payload (usually passed as parameter in a GET request to the app's load URL) and a client secret,
        authenticates the payload and returns the user's data, or False on fail.

        Uses constant-time str comparison to prevent vulnerability to timing attacks.
        """
        encoded_json, encoded_hmac = signed_payload.split('.')
        dc_json = base64.b64decode(encoded_json)
        signature = base64.b64decode(encoded_hmac)
        expected_sig = hmac.new(client_secret.encode(), base64.b64decode(encoded_json), hashlib.sha256).hexdigest()
        authorised = hmac.compare_digest(signature, expected_sig.encode())
        return loads(dc_json.decode()) if authorised else False

    @staticmethod
    def verify_payload_jwt(signed_payload, client_secret, client_id):
        """
        Given a signed payload JWT (usually passed as parameter in a GET request to the app's load URL)
        and a client secret, authenticates the payload and returns the user's data, or error on fail.
        """
        return jwt.decode(signed_payload,
                          client_secret,
                          algorithms=["HS256", "HS512"],
                          audience=client_id,
                          options={
                            'verify_iss': False
                          })

    async def fetch_token(self, client_secret, code, context, scope, redirect_uri,
                    token_url='https://login.bigcommerce.com/oauth2/token'):
        """
        Fetches a token from given token_url, using given parameters, and sets up session headers for
        future requests.
        redirect_uri should be the same as your callback URL.
        code, context, and scope should be passed as parameters to your callback URL on app installation.

        Raises HttpException on failure (same as Connection methods).
        """
        res = await self.post(token_url, {'client_id': self.client_id,
                                    'client_secret': client_secret,
                                    'code': code,
                                    'context': context,
                                    'scope': scope,
                                    'grant_type': 'authorization_code',
                                    'redirect_uri': redirect_uri},
                        headers={'Content-Type': 'application/x-www-form-urlencoded'})

        self.headers.update(self._oauth_headers(self.client_id, res['access_token']))
        return res

    def _handle_response(self, url, res, suppress_empty=True):
        """
        Adds rate limiting information on to the response object
        """
        result = Connection._handle_response(self, url, res, suppress_empty)
        if 'X-Rate-Limit-Time-Reset-Ms' in res.headers:
            self.rate_limit = dict(ms_until_reset=int(res.headers['X-Rate-Limit-Time-Reset-Ms']),
                                   window_size_ms=int(res.headers['X-Rate-Limit-Time-Window-Ms']),
                                   requests_remaining=int(res.headers['X-Rate-Limit-Requests-Left']),
                                   requests_quota=int(res.headers['X-Rate-Limit-Requests-Quota']))
            if self.rate_limiting_management:
                if self.rate_limiting_management['min_requests_remaining'] >= self.rate_limit['requests_remaining']:
                    if self.rate_limiting_management['wait']:
                        sleep(ceil(float(self.rate_limit['ms_until_reset']) / 1000))
                    if self.rate_limiting_management.get('callback_function'):
                        callback = self.rate_limiting_management['callback_function']
                        args_dict = self.rate_limiting_management.get('callback_args')
                        if args_dict:
                            callback(args_dict)
                        else:
                            callback()

        return result


class GraphQLConnection(OAuthConnection):
    def __init__(self, client_id, store_hash, access_token=None, host='api.bigcommerce.com',
                 api_path='/stores/{}/graphql', rate_limiting_management=None):
        self.client_id = client_id
        self.store_hash = store_hash
        self.host = host
        self.api_path = api_path
        self.graphql_path = "https://" + self.host + self.api_path.format(self.store_hash)
        self.timeout = 7.0  # can attach to session?
        self.rate_limiting_management = rate_limiting_management

        self.headers = {"Accept": "application/json",
                                 "Accept-Encoding": "gzip"}
        if access_token and store_hash:
            self.headers.update(self._oauth_headers(client_id, access_token))

        self._last_response = None  # for debugging

        self.rate_limit = {}

    def query(self, query, variables={}):
        return self.post(self.graphql_path, dict(query=query, variables=variables))

    def introspection_query(self):
        return self.query("""
        fragment FullType on __Type {
          kind
          name
          fields(includeDeprecated: true) {
            name
            args {
              ...InputValue
            }
            type {
              ...TypeRef
            }
            isDeprecated
            deprecationReason
          }
          inputFields {
            ...InputValue
          }
          interfaces {
            ...TypeRef
          }
          enumValues(includeDeprecated: true) {
            name
            isDeprecated
            deprecationReason
          }
          possibleTypes {
            ...TypeRef
          }
        }
        fragment InputValue on __InputValue {
          name
          type {
            ...TypeRef
          }
          defaultValue
        }
        fragment TypeRef on __Type {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
        query IntrospectionQuery {
          __schema {
            queryType {
              name
            }
            mutationType {
              name
            }
            types {
              ...FullType
            }
            directives {
              name
              locations
              args {
                ...InputValue
              }
            }
          }
        }
        """)