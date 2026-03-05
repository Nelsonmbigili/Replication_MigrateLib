### Explanation of Changes

To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import for `requests` was replaced with `treq`.
2. **Session Management**: The `Session` object from `requests` was removed, as `treq` does not require a session object for making requests.
3. **Request Method**: The method for making GET requests was changed from `self._sess.get(...)` to `treq.get(...)`.
4. **Error Handling**: The `ConnectionError` from `requests` was replaced with a generic `Exception` since `treq` raises different exceptions for connection issues.

The modified code is as follows:

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

import treq  # Changed from requests to treq

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

        # Removed session management as treq does not require it

    def _get_addr(self, _type):
        self.log.debug('_get_addr: type=%s', _type)
        try:
            resp = treq.get(self.urls[_type])  # Changed to treq.get
        except Exception:  # Changed from ConnectionError to a generic Exception
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