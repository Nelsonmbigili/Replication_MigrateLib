import time
import yaml
import logging
import json
import os
import aiohttp
import asyncio
from yaml.loader import SafeLoader

import cronitor

logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/49121365/implementing-retry-for-requests-in-python
def retry_session(retries, session=None, backoff_factor=0.3):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

JSON = 'json'
YAML = 'yaml'

class Monitor(object):
    _headers = {
        'User-Agent': 'cronitor-python',
    }

    @classmethod
    async def as_yaml(cls, api_key=None, api_version=None):
        timeout = cronitor.timeout or 10
        api_key = api_key or cronitor.api_key
        async with aiohttp.ClientSession() as session:
            async with session.get('%s.yaml' % cls._monitor_api_url(),
                                   auth=aiohttp.BasicAuth(api_key, ''),
                                   headers=dict(cls._headers, **{'Content-Type': 'application/yaml', 'Cronitor-Version': api_version}),
                                   timeout=timeout) as resp:
                if resp.status == 200:
                    return await resp.text()
                else:
                    raise cronitor.APIError("Unexpected error %s" % await resp.text())

    @classmethod
    async def put(cls, monitors=None, **kwargs):
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

        data = await cls._put(_monitors, api_key, rollback, request_format, api_version)

        if nested_format:
            return data

        _monitors = []
        for md in data:
            m = cls(md['key'])
            m.data = md
            _monitors.append(m)

        return _monitors if len(_monitors) > 1 else _monitors[0]

    @classmethod
    async def _put(cls, monitors, api_key, rollback, request_format, api_version):
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

        async with aiohttp.ClientSession() as session:
            async with session.put(url,
                                   auth=aiohttp.BasicAuth(api_key, ''),
                                   data=data,
                                   headers=dict(cls._headers, **{'Content-Type': content_type, 'Cronitor-Version': api_version}),
                                   timeout=timeout) as resp:
                if resp.status == 200:
                    if request_format == YAML:
                        return yaml.load(await resp.text(), Loader=SafeLoader)
                    else:
                        return (await resp.json()).get('monitors', [])
                elif resp.status == 400:
                    raise cronitor.APIValidationError(await resp.text())
                else:
                    raise cronitor.APIError("Unexpected error %s" % await resp.text())

    def __init__(self, key, api_key=None, api_version=None, env=None):
        self.key = key
        self.api_key = api_key or cronitor.api_key
        self.api_verion = api_version or cronitor.api_version
        self.env = env or cronitor.environment
        self._data = None

    @property
    async def data(self):
        if self._data and type(self._data) is not Struct:
            self._data = Struct(**self._data)
        elif not self._data:
            self._data = Struct(**await self._fetch())
        return self._data

    @data.setter
    def data(self, data):
        self._data = Struct(**data)

    async def delete(self):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                        self._monitor_api_url(self.key),
                        auth=aiohttp.BasicAuth(self.api_key, ''),
                        headers=self._headers,
                        timeout=10) as resp:
                if resp.status == 204:
                    return True
                elif resp.status == 404:
                    raise cronitor.MonitorNotFound("Monitor '%s' not found" % self.key)
                else:
                    raise cronitor.APIError("An unexpected error occurred when deleting '%s'" % self.key)

    async def ping(self, **params):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        async with aiohttp.ClientSession() as session:
            return await session.get(url=self._ping_api_url(), params=self._clean_params(params), timeout=5, headers=self._headers)

    def ok(self):
        asyncio.run(self.ping(state=cronitor.State.OK))

    async def pause(self, hours):
        if not self.api_key:
            logger.error('No API key detected. Set cronitor.api_key or initialize Monitor with kwarg api_key.')
            return

        async with aiohttp.ClientSession() as session:
            return await session.get(url='{}/pause/{}'.format(self._monitor_api_url(self.key), hours), auth=aiohttp.BasicAuth(self.api_key, ''), timeout=5, headers=self._headers)

    async def unpause(self):
        return await self.pause(0)

    async def _fetch(self):
        if not self.api_key:
            raise cronitor.AuthenticationError('No api_key detected. Set cronitor.api_key or initialize Monitor with kwarg.')

        async with aiohttp.ClientSession() as session:
            async with session.get(self._monitor_api_url(self.key),
                                   timeout=10,
                                   auth=aiohttp.BasicAuth(self.api_key, ''),
                                   headers=dict(self._headers, **{'Content-Type': 'application/json', 'Cronitor-Version': self.api_verion})) as resp:
                if resp.status == 404:
                    raise cronitor.MonitorNotFound("Monitor '%s' not found" % self.key)
                return await resp.json()

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