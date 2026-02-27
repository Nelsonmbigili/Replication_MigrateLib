import time
import yaml
import logging
import json
import os
import cronitor
from yaml.loader import SafeLoader
from urllib3 import PoolManager
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Retry session using urllib3
def retry_session(retries, backoff_factor=0.3):
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
    )
    return PoolManager(retries=retry)

JSON = 'json'
YAML = 'yaml'

class Monitor(object):
    _headers = {
        'User-Agent': 'cronitor-python',
    }

    _req = retry_session(retries=3)

    @classmethod
    def as_yaml(cls, api_key=None, api_version=None):
        timeout = cronitor.timeout or 10
        api_key = api_key or cronitor.api_key
        url = '%s.yaml' % cls._monitor_api_url()
        headers = dict(cls._headers, **{'Content-Type': 'application/yaml', 'Cronitor-Version': api_version})
        headers['Authorization'] = f'Basic {api_key}:'

        resp = cls._req.request('GET', url, headers=headers, timeout=timeout)
        if resp.status == 200:
            return resp.data.decode('utf-8')
        else:
            raise cronitor.APIError("Unexpected error %s" % resp.data.decode('utf-8'))

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

        headers = dict(cls._headers, **{'Content-Type': content_type, 'Cronitor-Version': api_version})
        headers['Authorization'] = f'Basic {api_key}:'

        resp = cls._req.request('PUT', url, body=data, headers=headers, timeout=timeout)

        if resp.status == 200:
            if request_format == YAML:
                return yaml.load(resp.data.decode('utf-8'), Loader=SafeLoader)
            else:
                return json.loads(resp.data.decode('utf-8')).get('monitors', [])
        elif resp.status == 400:
            raise cronitor.APIValidationError(resp.data.decode('utf-8'))
        else:
            raise cronitor.APIError("Unexpected error %s" % resp.data.decode('utf-8'))

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
        url = self._monitor_api_url(self.key)
        headers = self._headers
        headers['Authorization'] = f'Basic {self.api_key}:'

        resp = self._req.request('DELETE', url, headers=headers, timeout=10)

        if resp.status == 204:
            return True
        elif resp.status == 404:
            raise cronitor.MonitorNotFound("Monitor '%s' not found" % self.key)
        else:
            raise cronitor.APIError("An unexpected error occured when deleting '%s'" % self.key)

    def ping(self, **params):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        url = self._ping_api_url()
        headers = self._headers
        headers['Authorization'] = f'Basic {self.api_key}:'
        resp = self._req.request('GET', url, fields=self._clean_params(params), headers=headers, timeout=5)
        return resp

    def ok(self):
        self.ping(state=cronitor.State.OK)

    def pause(self, hours):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        url = '{}/pause/{}'.format(self._monitor_api_url(self.key), hours)
        headers = self._headers
        headers['Authorization'] = f'Basic {self.api_key}:'
        return self._req.request('GET', url, headers=headers, timeout=5)

    def unpause(self):
        return self.pause(0)

    def _fetch(self):
        if not self.api_key:
            raise cronitor.AuthenticationError('No api_key detected. Set cronitor.api_key or initialize Monitor with kwarg.')

        url = self._monitor_api_url(self.key)
        headers = dict(self._headers, **{'Content-Type': 'application/json', 'Cronitor-Version': self.api_verion})
        headers['Authorization'] = f'Basic {self.api_key}:'

        resp = self._req.request('GET', url, headers=headers, timeout=10)

        if resp.status == 404:
            raise cronitor.MonitorNotFound("Monitor '%s' not found" % self.key)
        return json.loads(resp.data.decode('utf-8'))

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
