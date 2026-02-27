### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Changes**: Replaced the import of `Session` and `ConnectionError` from `requests` with their equivalents from `requests_futures`.
2. **Session Replacement**: Replaced the `Session` object from `requests` with `FuturesSession` from `requests_futures`. This allows for asynchronous HTTP requests.
3. **Synchronous Behavior**: Since the original code uses synchronous requests, the `.result()` method of the `Future` object returned by `FuturesSession.get()` is used to block until the request completes, maintaining the original synchronous behavior.
4. **No Other Changes**: The rest of the code remains unchanged to ensure compatibility with the larger application.

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

from requests_futures.sessions import FuturesSession
from requests.exceptions import ConnectionError

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

        self._sess = FuturesSession()
        self._sess.headers.update(
            {
                'User-Agent': f'octodns/{octodns_version} octodns-ddns/{__VERSION__}'
            }
        )

    def _get_addr(self, _type):
        self.log.debug('_get_addr: type=%s', _type)
        try:
            # Use FuturesSession to make the request
            future = self._sess.get(self.urls[_type])
            resp = future.result()  # Block until the request completes
        except ConnectionError:
            raise Exception(
                'Failed to get ip address for type={}'.format(_type)
            )
        resp.raise_for_status()
        addr = resp.content.decode('utf-8')
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
- Replaced `Session` with `FuturesSession` from `requests_futures`.
- Used `.result()` to block and retrieve the response, preserving the synchronous behavior of the original code.
- No other changes were made to the logic, structure, or style of the code.