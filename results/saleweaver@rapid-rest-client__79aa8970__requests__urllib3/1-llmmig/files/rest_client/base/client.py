import json
import logging
import os
from json import JSONDecodeError
from urllib.parse import urljoin
import urllib3

from rest_client.base.authentication import Authentication
from rest_client.base.util import fill_query_params
from rest_client.log_config import logger_config
from rest_client.base.config import BaseUrlConfig, RequestConfig, ApiResponse
from rest_client.base.variables import CONTENT_TYPE, ENV
from rest_client.__version__ import __version__
from rest_client.base.exceptions import ApiException

log = logger_config(__name__, logging.INFO)


class NoEndpointsExceptions(Exception):
    pass


class Client:
    user_agent = f'saleweaver-base-client-{__version__}'

    @property
    def endpoints(self) -> dict:
        return self._endpoints

    @endpoints.setter
    def endpoints(self, endpoints):
        self._endpoints = endpoints

    @property
    def base_url_config(self) -> BaseUrlConfig:
        return self._base_url_config

    @base_url_config.setter
    def base_url_config(self, base_url_config: BaseUrlConfig):
        self._base_url_config = base_url_config

    def __init__(self, authentication_handler: Authentication = None):
        self._endpoints = {}
        self._base_url_config = None
        self.auth = authentication_handler
        self.method: str = 'GET'
        self.content_type: str = os.environ.get(CONTENT_TYPE, 'application/json;charset=UTF-8')
        self.http = urllib3.PoolManager()  # Initialize urllib3 PoolManager

    @property
    def headers(self):
        return {
            'Content-Type': self.content_type,
            'User-Agent': self.user_agent
        }

    def _path(self, path):
        path = path.lstrip('/')
        if os.environ.get(ENV, None) == 'SANDBOX':
            return urljoin(self.base_url_config.sandbox_url, path)
        return urljoin(self.base_url_config.base_url, path)

    def _request(self, data: dict, *args, **kwargs) -> ApiResponse:
        request_config: RequestConfig = data.pop('request_config')
        log.debug(request_config)
        self._log_request(args, data, kwargs, request_config)

        # Prepare request parameters
        method = request_config.method
        url = self._path(request_config.path)
        headers = kwargs.pop('headers', self.headers)
        body = None
        fields = None

        if method in ('POST', 'PUT', 'PATCH'):
            body = data.get('payload') or json.dumps(data)
        elif method in ('GET', 'DELETE'):
            fields = data

        # Make the HTTP request using urllib3
        res = self.http.request(
            method,
            url,
            headers=headers,
            body=body,
            fields=fields
        )

        self._log_response(res)

        # Handle the response
        try:
            response_data = res.data.decode('utf-8')  # Decode response data
            response = json.loads(response_data)  # Attempt to parse JSON
        except (JSONDecodeError, ValueError):  # Handle JSON parsing errors
            response = res.data.decode('utf-8')  # Fallback to raw content

        if 200 <= res.status < 400:
            return ApiResponse(response, res.headers, res.status)
        raise ApiException(response, res.headers, res.status)

    def _log_request(self, args, data, kwargs, request_config):
        log.debug('Requesting %s', (self._path(request_config.path)))
        log.debug(kwargs.get('headers', self.headers))
        log.debug(request_config)
        log.debug(data)
        log.debug(args)
        log.debug(kwargs)

    def _log_response(self, res):
        log.debug(res.headers)
        log.debug(res.status)
        log.debug(res.data)

    def __getattr__(self, item):
        log.debug(f'Requesting endpoint: {item}')
        log.debug(self.endpoints)

        if self.endpoints.get(item, None):
            def wrapper(*args, **kwargs):
                log.debug('called with %r and %r' % (args, kwargs))
                return self.method_template(self.endpoints.get(item))(*args, **kwargs)

            return wrapper
        raise AttributeError(f'{item} does not exist, possible calls: {self.endpoints.keys()}')

    def method_template(self, _endpoint):
        def fn(*args, **kwargs):
            _endpoint.path = fill_query_params(_endpoint.path, *args)
            kwargs.update({
                'request_config': _endpoint
            })
            return self._request(kwargs)

        return fn
