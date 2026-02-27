import json
import logging
import os
from json import JSONDecodeError
from urllib.parse import urljoin
import pycurl
from io import BytesIO

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

        # Prepare the URL, headers, and data
        url = self._path(request_config.path)
        headers = kwargs.pop('headers', self.headers)
        headers_list = [f"{key}: {value}" for key, value in headers.items()]
        payload = data.get('payload') or json.dumps(data) if data and request_config.method in ('POST', 'PUT', 'PATCH') else None

        # Initialize pycurl
        curl = pycurl.Curl()
        response_buffer = BytesIO()
        header_buffer = BytesIO()

        try:
            # Set URL
            curl.setopt(pycurl.URL, url)

            # Set HTTP method
            if request_config.method == 'POST':
                curl.setopt(pycurl.POST, 1)
                if payload:
                    curl.setopt(pycurl.POSTFIELDS, payload)
            elif request_config.method in ('PUT', 'PATCH'):
                curl.setopt(pycurl.CUSTOMREQUEST, request_config.method)
                if payload:
                    curl.setopt(pycurl.POSTFIELDS, payload)
            elif request_config.method == 'DELETE':
                curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
            elif request_config.method == 'GET':
                if data:
                    # Append query parameters to the URL
                    query_params = '&'.join([f"{key}={value}" for key, value in data.items()])
                    curl.setopt(pycurl.URL, f"{url}?{query_params}")

            # Set headers
            curl.setopt(pycurl.HTTPHEADER, headers_list)

            # Capture response body and headers
            curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
            curl.setopt(pycurl.HEADERFUNCTION, header_buffer.write)

            # Perform the request
            curl.perform()

            # Extract response details
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            response_body = response_buffer.getvalue().decode('utf-8')
            response_headers = header_buffer.getvalue().decode('utf-8')

            self._log_response(response_body, status_code, response_headers)

            # Parse the response
            try:
                response = json.loads(response_body)
            except JSONDecodeError:
                response = response_body

            if 200 <= status_code < 400:
                return ApiResponse(response, response_headers, status_code)
            raise ApiException(response, response_headers, status_code)

        except pycurl.error as e:
            raise ApiException(f"Network error: {e}", {}, 0)

        finally:
            # Clean up
            curl.close()

    def _log_request(self, args, data, kwargs, request_config):
        log.debug('Requesting %s', (self._path(request_config.path)))
        log.debug(kwargs.get('headers', self.headers))
        log.debug(request_config)
        log.debug(data)
        log.debug(args)
        log.debug(kwargs)

    def _log_response(self, response_body, status_code, response_headers):
        log.debug(f"Response status: {status_code}")
        log.debug(f"Response headers: {response_headers}")
        log.debug(f"Response body: {response_body}")

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
