import time
import yaml
import logging
import json
import os
import pycurl
from io import BytesIO
from yaml.loader import SafeLoader

import cronitor

logger = logging.getLogger(__name__)

JSON = 'json'
YAML = 'yaml'

class Monitor(object):
    _headers = {
        'User-Agent': 'cronitor-python',
    }

    @staticmethod
    def _make_request(method, url, headers=None, auth=None, data=None, timeout=10):
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.setopt(pycurl.TIMEOUT, timeout)

        # Set HTTP method
        if method == 'GET':
            curl.setopt(pycurl.CUSTOMREQUEST, 'GET')
        elif method == 'PUT':
            curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
            if data:
                curl.setopt(pycurl.POSTFIELDS, data)
        elif method == 'DELETE':
            curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')

        # Set headers
        if headers:
            curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

        # Set authentication
        if auth:
            curl.setopt(pycurl.USERPWD, f"{auth[0]}:{auth[1]}")

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            response_body = buffer.getvalue().decode('utf-8')
        except pycurl.error as e:
            raise cronitor.APIError(f"An error occurred: {e}")
        finally:
            curl.close()

        return status_code, response_body

    @classmethod
    def as_yaml(cls, api_key=None, api_version=None):
        timeout = cronitor.timeout or 10
        api_key = api_key or cronitor.api_key
        url = f"{cls._monitor_api_url()}.yaml"
        headers = dict(cls._headers, **{'Content-Type': 'application/yaml', 'Cronitor-Version': api_version})
        status_code, response_body = cls._make_request(
            method='GET',
            url=url,
            headers=headers,
            auth=(api_key, ''),
            timeout=timeout
        )
        if status_code == 200:
            return response_body
        else:
            raise cronitor.APIError(f"Unexpected error {response_body}")

    @classmethod
    def put(cls, monitors=None, **kwargs):
        api_key = cronitor.api_key
        api_version = cronitor.api_version
        request_format = JSON

        rollback = False
        if 'rollback' in kwargs:
            rollback = kwargs['rollback']
            del kwargs['rollback']
        if 'api_key' in kwargs:
            api_key = kwargs['api_key']
            del kwargs['api_key']
        if 'api_version' in kwargs:
            api_version = kwargs['api_version']
            del kwargs['api_version']
        if 'format' in kwargs:
            request_format = kwargs['format']
            del kwargs['format']

        _monitors = monitors or [kwargs]
        nested_format = True if type(monitors) == dict else False

        data = cls._put(_monitors, api_key, rollback, request_format, api_version)

        if nested_format:
            return data

        _monitors = []
        for md in data:
            m = cls(md['key'])
            m.data = md
            _monitors.append(m)

        return _monitors if len(_monitors) > 1 else _monitors[0]

    @classmethod
    def _put(cls, monitors, api_key, rollback, request_format, api_version):
        timeout = cronitor.timeout or 10
        payload = _prepare_payload(monitors, rollback, request_format)
        if request_format == YAML:
            content_type = 'application/yaml'
            data = yaml.dump(payload)
            url = f"{cls._monitor_api_url()}.yaml"
        else:
            content_type = 'application/json'
            data = json.dumps(payload)
            url = cls._monitor_api_url()

        headers = dict(cls._headers, **{'Content-Type': content_type, 'Cronitor-Version': api_version})
        status_code, response_body = cls._make_request(
            method='PUT',
            url=url,
            headers=headers,
            auth=(api_key, ''),
            data=data,
            timeout=timeout
        )

        if status_code == 200:
            if request_format == YAML:
                return yaml.load(response_body, Loader=SafeLoader)
            else:
                return json.loads(response_body).get('monitors', [])
        elif status_code == 400:
            raise cronitor.APIValidationError(response_body)
        else:
            raise cronitor.APIError(f"Unexpected error {response_body}")

    def delete(self):
        url = self._monitor_api_url(self.key)
        status_code, response_body = self._make_request(
            method='DELETE',
            url=url,
            auth=(self.api_key, ''),
            headers=self._headers,
            timeout=10
        )

        if status_code == 204:
            return True
        elif status_code == 404:
            raise cronitor.MonitorNotFound(f"Monitor '{self.key}' not found")
        else:
            raise cronitor.APIError(f"An unexpected error occurred when deleting '{self.key}'")

    def _fetch(self):
        if not self.api_key:
            raise cronitor.AuthenticationError('No api_key detected. Set cronitor.api_key or initialize Monitor with kwarg.')

        url = self._monitor_api_url(self.key)
        headers = dict(self._headers, **{'Content-Type': 'application/json', 'Cronitor-Version': self.api_verion})
        status_code, response_body = self._make_request(
            method='GET',
            url=url,
            auth=(self.api_key, ''),
            headers=headers,
            timeout=10
        )

        if status_code == 404:
            raise cronitor.MonitorNotFound(f"Monitor '{self.key}' not found")
        return json.loads(response_body)

    @classmethod
    def _monitor_api_url(cls, key=None):
        if not key: return "https://cronitor.io/api/monitors"
        return f"https://cronitor.io/api/monitors/{key}"

def _prepare_payload(monitors, rollback=False, request_format=JSON):
    ret = {}
    if request_format == JSON:
        ret['monitors'] = monitors
    if request_format == YAML:
        ret = monitors
    if rollback:
        ret['rollback'] = True
    return ret


class Struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
