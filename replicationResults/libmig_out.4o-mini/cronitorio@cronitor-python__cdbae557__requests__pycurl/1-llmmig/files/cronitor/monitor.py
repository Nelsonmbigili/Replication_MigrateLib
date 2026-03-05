import time
import yaml
import logging
import json
import os
import pycurl
from io import BytesIO
from yaml.loader import SafeLoader

import cronitor
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def retry_session(retries, session=None, backoff_factor=0.3):
    # Note: The retry logic is not applicable for pycurl in the same way as requests.
    pass

JSON = 'json'
YAML = 'yaml'

class Monitor(object):
    _headers = {
        'User-Agent': 'cronitor-python',
    }

    @classmethod
    def as_yaml(cls, api_key=None, api_version=None):
        timeout = cronitor.timeout or 10
        api_key = api_key or cronitor.api_key
        url = '%s.yaml' % cls._monitor_api_url()
        response = cls._make_request('GET', url, api_key, api_version, timeout, content_type='application/yaml')
        return response

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
            url = '{}.yaml'.format(cls._monitor_api_url())
        else:
            content_type = 'application/json'
            data = json.dumps(payload)
            url = cls._monitor_api_url()

        response = cls._make_request('PUT', url, api_key, api_version, timeout, data=data, content_type=content_type)

        if request_format == YAML:
            return yaml.load(response, Loader=SafeLoader)
        else:
            return json.loads(response).get('monitors', [])

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

    def delete(self):
        response = self._make_request('DELETE', self._monitor_api_url(self.key), self.api_key)
        if response is None:
            return True
        elif response == 404:
            raise cronitor.MonitorNotFound("Monitor '%s' not found" % self.key)
        else:
            raise cronitor.APIError("An unexpected error occurred when deleting '%s'" % self.key)

    def ping(self, **params):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        return self._make_request('GET', self._ping_api_url(), self.api_key, params=self._clean_params(params))

    def ok(self):
        self.ping(state=cronitor.State.OK)

    def pause(self, hours):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        return self._make_request('GET', '{}/pause/{}'.format(self._monitor_api_url(self.key), hours), self.api_key)

    def unpause(self):
        return self.pause(0)

    def _fetch(self):
        if not self.api_key:
            raise cronitor.AuthenticationError('No api_key detected. Set cronitor.api_key or initialize Monitor with kwarg.')

        response = self._make_request('GET', self._monitor_api_url(self.key), self.api_key)
        if response == 404:
            raise cronitor.MonitorNotFound("Monitor '%s' not found" % self.key)
        return json.loads(response)

    def _clean_params(self, params):
        metrics = None
        if 'metrics' in params and type(params['metrics']) == dict:
            metrics = ['{}:{}'.format(k,v) for k,v in params['metrics'].items()]

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
        return "https://cronitor.link/p/{}/{}".format(self.api_key, self.key)

    @classmethod
    def _monitor_api_url(cls, key=None):
        if not key: return "https://cronitor.io/api/monitors"
        return "https://cronitor.io/api/monitors/{}".format(key)

    @classmethod
    def _make_request(cls, method, url, api_key, api_version=None, timeout=10, data=None, content_type=None, params=None):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.setopt(c.TIMEOUT, timeout)
        c.setopt(c.HTTPAUTH, c.HTTPAUTH_BASIC)
        c.setopt(c.USERPWD, f"{api_key}:")
        
        if content_type:
            headers = [f'Content-Type: {content_type}', 'Cronitor-Version: {}'.format(api_version)]
            c.setopt(c.HTTPHEADER, headers)

        if method == 'POST':
            c.setopt(c.POSTFIELDS, data)
        elif method == 'PUT':
            c.setopt(c.CUSTOMREQUEST, 'PUT')
            c.setopt(c.POSTFIELDS, data)
        elif method == 'DELETE':
            c.setopt(c.CUSTOMREQUEST, 'DELETE')

        if params:
            query_string = '&'.join([f"{key}={value}" for key, value in params.items() if value is not None])
            c.setopt(c.URL, f"{url}?{query_string}")

        try:
            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            response_data = buffer.getvalue().decode('utf-8')
            if response_code == 200:
                return response_data
            else:
                return response_code
        finally:
            c.close()

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
