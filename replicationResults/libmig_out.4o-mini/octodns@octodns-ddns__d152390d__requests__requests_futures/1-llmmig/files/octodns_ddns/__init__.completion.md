### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: The `Session` class was imported from `requests_futures.sessions` instead of `requests`.
2. **Using Futures**: The `get` method of the session was replaced with `get` from `requests_futures.sessions`, which returns a `Future` object. This allows for asynchronous requests.
3. **Handling the Response**: Since the response is now a `Future`, we need to call `.result()` on it to get the actual response object before proceeding to check for errors or read the content.

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
            future = self._sess.get(self.urls[_type])
            resp = future.result()  # Get the actual response
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

This code now uses `requests_futures` to handle asynchronous HTTP requests while maintaining the original structure and functionality.