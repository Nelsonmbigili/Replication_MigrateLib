### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statements**: The `Session` class from `requests` was replaced with `urllib3.PoolManager` for managing connections.
2. **Session Management**: The `Session` object was replaced with a `PoolManager` instance, which is used to make HTTP requests.
3. **Making Requests**: The `get` method of the `Session` object was replaced with the `urlopen` method of the `PoolManager`. The response handling was adjusted accordingly.
4. **Error Handling**: The `ConnectionError` from `requests` was replaced with `urllib3.exceptions.HTTPError` for handling connection issues.
5. **Response Content**: The way to access the response content was changed from `resp.content` to `resp.data`.

Here is the modified code:

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
import urllib3
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

        self._http = urllib3.PoolManager()
        self._headers = {
            'User-Agent': f'octodns/{octodns_version} octodns-ddns/{__VERSION__}'
        }

    def _get_addr(self, _type):
        self.log.debug('_get_addr: type=%s', _type)
        try:
            resp = self._http.request('GET', self.urls[_type], headers=self._headers)
        except HTTPError:
            raise Exception(
                'Failed to get ip address for type={}'.format(_type)
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