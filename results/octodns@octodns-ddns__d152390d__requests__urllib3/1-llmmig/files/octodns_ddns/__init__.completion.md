### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Session Replacement**: The `requests.Session` object was replaced with an `urllib3.PoolManager` object, which provides connection pooling and is the closest equivalent in `urllib3`.
2. **HTTP Requests**: The `Session.get` method was replaced with `PoolManager.request` using the `GET` method.
3. **Error Handling**: The `requests.exceptions.ConnectionError` was replaced with `urllib3.exceptions.HTTPError` for handling connection-related errors.
4. **Response Handling**: The `requests` library's `Response` object methods (`raise_for_status` and `content.decode`) were replaced with equivalent handling in `urllib3`. Specifically:
   - `raise_for_status` was replaced with manual status code checks (`response.status != 200`).
   - `response.content.decode('utf-8')` was replaced with `response.data.decode('utf-8')`.

### Modified Code
```python
'''
A simple Dynamic DNS source for octoDNS.

Supports both IPv4 and IPv6 addresses. Generally useful when you have a zone
with staticly configured records but would also like to include a dynamic
record, e.g. for your office or home on a non-fixed IP address.
'''

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from logging import getLogger

from urllib3 import PoolManager
from urllib3.exceptions import HTTPError

from octodns import __VERSION__ as octodns_version
from octodns.record import Record
from octodns.source.base import BaseSource

# TODO: remove __VERSION__ with the next major version release
__version__ = __VERSION__ = '0.2.1'


class DdnsSource(BaseSource):
    SUPPORTS_GEO = False
    SUPPORTS = ('A', 'AAAA')

    def __init__(self, id, types=('A', 'AAAA'), urls={}, ttl=60):
        self.log = getLogger('DdnsSource[{}]'.format(id))
        self.log.debug('__init__: id=%s, types=%s, ttl=%d', id, types, ttl)
        super().__init__(id)
        self.types = types
        self.ttl = ttl
        self.urls = {
            'A': urls.get('A', 'https://v4.ident.me/'),
            'AAAA': urls.get('AAAA', 'https://v6.ident.me/'),
        }

        self._http = PoolManager(headers={
            'User-Agent': f'octodns/{octodns_version} octodns-ddns/{__VERSION__}'
        })

    def _get_addr(self, _type):
        self.log.debug('_get_addr: type=%s', _type)
        try:
            resp = self._http.request('GET', self.urls[_type])
        except HTTPError:
            raise Exception(
                'Failed to get ip address for type={}'.format(_type)
            )
        if resp.status != 200:
            raise Exception(
                'Failed to get ip address for type={}: HTTP {}'.format(
                    _type, resp.status
                )
            )
        addr = resp.data.decode('utf-8')
        self.log.info('_get_addr: type=%s is %s', _type, addr)
        return addr

    def populate(self, zone, target=False, lenient=False):
        self.log.debug('populate: zone=%s', zone.name)
        before = len(zone.records)

        for _type in self.types:
            addr = self._get_addr(_type)
            if addr:
                record = Record.new(
                    zone,
                    self.id,
                    {'ttl': self.ttl, 'type': _type, 'value': addr},
                    source=self,
                )
                zone.add_record(record)

        self.log.info(
            'populate:   found %s records', len(zone.records) - before
        )
```

### Summary of Changes
- Replaced `requests.Session` with `urllib3.PoolManager`.
- Updated HTTP request calls to use `PoolManager.request`.
- Replaced `requests.exceptions.ConnectionError` with `urllib3.exceptions.HTTPError`.
- Manually checked HTTP response status codes instead of using `raise_for_status`.
- Updated response content decoding to use `response.data.decode('utf-8')`.