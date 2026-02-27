import time
import yaml
import logging
import json
import os
import treq
from yaml.loader import SafeLoader
from twisted.internet.defer import inlineCallbacks, returnValue

import cronitor

logger = logging.getLogger(__name__)

JSON = 'json'
YAML = 'yaml'

class Monitor(object):
    _headers = {
        'User-Agent': 'cronitor-python',
    }

    @classmethod
    @inlineCallbacks
    def as_yaml(cls, api_key=None, api_version=None):
        timeout = cronitor.timeout or 10
        api_key = api_key or cronitor.api_key
        url = f"{cls._monitor_api_url()}.yaml"
        headers = dict(cls._headers, **{'Content-Type': 'application/yaml', 'Cronitor-Version': api_version})
        response = yield treq.get(url, auth=(api_key, ''), headers=headers, timeout=timeout)
        if response.code == 200:
            text = yield response.text()
            returnValue(text)
        else:
            text = yield response.text()
            raise cronitor.APIError(f"Unexpected error {text}")

    @classmethod
    @inlineCallbacks
    def put(cls, monitors=None, **kwargs):
        api_key = cronitor.api_key
        api_version = cronitor.api_version
        request_format = JSON

        rollback = kwargs.pop('rollback', False)
        api_key = kwargs.pop('api_key', api_key)
        api_version = kwargs.pop('api_version', api_version)
        request_format = kwargs.pop('format', request_format)

        _monitors = monitors or [kwargs]
        nested_format = isinstance(monitors, dict)

        data = yield cls._put(_monitors, api_key, rollback, request_format, api_version)

        if nested_format:
            returnValue(data)

        _monitors = []
        for md in data:
            m = cls(md['key'])
            m.data = md
            _monitors.append(m)

        returnValue(_monitors if len(_monitors) > 1 else _monitors[0])

    @classmethod
    @inlineCallbacks
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
        response = yield treq.put(url, auth=(api_key, ''), data=data, headers=headers, timeout=timeout)

        if response.code == 200:
            text = yield response.text()
            if request_format == YAML:
                returnValue(yaml.load(text, Loader=SafeLoader))
            else:
                json_data = yield response.json()
                returnValue(json_data.get('monitors', []))
        elif response.code == 400:
            text = yield response.text()
            raise cronitor.APIValidationError(text)
        else:
            text = yield response.text()
            raise cronitor.APIError(f"Unexpected error {text}")

    def __init__(self, key, api_key=None, api_version=None, env=None):
        self.key = key
        self.api_key = api_key or cronitor.api_key
        self.api_verion = api_version or cronitor.api_version
        self.env = env or cronitor.environment
        self._data = None

    @property
    def data(self):
        if self._data and type(self._data) is not Struct:
            self._data = Struct(**self._data)
        elif not self._data:
            self._data = Struct(**self._fetch())
        return self._data

    @data.setter
    def data(self, data):
        self._data = Struct(**data)

    @inlineCallbacks
    def delete(self):
        url = self._monitor_api_url(self.key)
        response = yield treq.delete(url, auth=(self.api_key, ''), headers=self._headers, timeout=10)

        if response.code == 204:
            returnValue(True)
        elif response.code == 404:
            raise cronitor.MonitorNotFound(f"Monitor '{self.key}' not found")
        else:
            raise cronitor.APIError(f"An unexpected error occurred when deleting '{self.key}'")

    @inlineCallbacks
    def ping(self, **params):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        url = self._ping_api_url()
        response = yield treq.get(url, params=self._clean_params(params), timeout=5, headers=self._headers)
        returnValue(response)

    @inlineCallbacks
    def pause(self, hours):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        url = f"{self._monitor_api_url(self.key)}/pause/{hours}"
        response = yield treq.get(url, auth=(self.api_key, ''), timeout=5, headers=self._headers)
        returnValue(response)

    def unpause(self):
        return self.pause(0)

    @inlineCallbacks
    def _fetch(self):
        if not self.api_key:
            raise cronitor.AuthenticationError('No api_key detected. Set cronitor.api_key or initialize Monitor with kwarg.')

        url = self._monitor_api_url(self.key)
        headers = dict(self._headers, **{'Content-Type': 'application/json', 'Cronitor-Version': self.api_verion})
        response = yield treq.get(url, timeout=10, auth=(self.api_key, ''), headers=headers)

        if response.code == 404:
            raise cronitor.MonitorNotFound(f"Monitor '{self.key}' not found")
        json_data = yield response.json()
        returnValue(json_data)

    def _clean_params(self, params):
        metrics = None
        if 'metrics' in params and isinstance(params['metrics'], dict):
            metrics = [f"{k}:{v}" for k, v in params['metrics'].items()]

        return {
            'state': params.get('state', None),
            'message': params.get('message', None),
            'series': params.get('series', None),
            'host': params.get('host', os.getenv('COMPUTERNAME', None)),
            'metric': metrics,
            'stamp': time.time(),
            'env': self.env,
        }

    def _ping_api_url(self):
        return f"https://cronitor.link/p/{self.api_key}/{self.key}"

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
