### Explanation of Changes

To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Session Management**: The `httpx` library does not require a separate session management setup like `requests`. Therefore, the retry logic was adjusted to work directly with `httpx`.
3. **Method Calls**: The method calls for `get`, `put`, and `delete` were updated to use `httpx` syntax. The `httpx` library uses `response.status_code` in the same way as `requests`, so no changes were needed there.
4. **Timeout Handling**: The timeout parameter is passed directly in the same way as `requests`, so it remains unchanged.
5. **Response Handling**: The response handling for JSON and text responses remains the same, as `httpx` provides similar methods.

Here is the modified code:

```python
import time
import yaml
import logging
import json
import os
import httpx
from yaml.loader import SafeLoader


import cronitor
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/49121365/implementing-retry-for-requests-in-python
def retry_session(retries, backoff_factor=0.3):
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
    )
    return httpx.Client(retries=retry)

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
        resp = cls._req.get('%s.yaml' % cls._monitor_api_url(),
                        auth=(api_key, ''),
                        headers=dict(cls._headers, **{'Content-Type': 'application/yaml', 'Cronitor-Version': api_version}),
                        timeout=timeout)
        if resp.status_code == 200:
            return resp.text
        else:
            raise cronitor.APIError("Unexpected error %s" % resp.text)

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

        resp = cls._req.put(url,
                        auth=(api_key, ''),
                        data=data,
                        headers=dict(cls._headers, **{'Content-Type': content_type, 'Cronitor-Version': api_version}),
                        timeout=timeout)

        if resp.status_code == 200:
            if request_format == YAML:
                return yaml.load(resp.text, Loader=SafeLoader)
            else:
                return resp.json().get('monitors', [])
        elif resp.status_code == 400:
            raise cronitor.APIValidationError(resp.text)
        else:
            raise cronitor.APIError("Unexpected error %s" % resp.text)

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
        resp = httpx.delete(
                    self._monitor_api_url(self.key),
                    auth=(self.api_key, ''),
                    headers=self._headers,
                    timeout=10)

        if resp.status_code == 204:
            return True
        elif resp.status_code == 404:
            raise cronitor.MonitorNotFound("Monitor '%s' not found" % self.key)
        else:
            raise cronitor.APIError("An unexpected error occured when deleting '%s'" % self.key)

    def ping(self, **params):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        return self._req.get(url=self._ping_api_url(), params=self._clean_params(params), timeout=5, headers=self._headers)

    def ok(self):
        self.ping(state=cronitor.State.OK)

    def pause(self, hours):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        return self._req.get(url='{}/pause/{}'.format(self._monitor_api_url(self.key), hours), auth=(self.api_key, ''), timeout=5, headers=self._headers)

    def unpause(self):
        return self.pause(0)

    def _fetch(self):
        if not self.api_key:
            raise cronitor.AuthenticationError('No api_key detected. Set cronitor.api_key or initialize Monitor with kwarg.')

        resp = httpx.get(self._monitor_api_url(self.key),
                            timeout=10,
                            auth=(self.api_key, ''),
                            headers=dict(self._headers, **{'Content-Type': 'application/json', 'Cronitor-Version': self.api_verion}))

        if resp.status_code == 404:
            raise cronitor.MonitorNotFound("Monitor '%s' not found" % self.key)
        return resp.json()

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

```