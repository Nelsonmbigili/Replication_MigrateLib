### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Session Replacement**: The `requests.Session` object was replaced with `treq`'s asynchronous HTTP request methods. Since `treq` is built on `Twisted`, it does not use a session object in the same way as `requests`.
2. **Asynchronous Methods**: `treq` is asynchronous, so the `_get_addr` method was modified to be an `async` function. This required adding `await` for the `treq.get` call and decoding the response content.
3. **Error Handling**: `treq` raises exceptions differently. The `ConnectionError` from `requests` was replaced with `twisted.internet.error` exceptions, and the `raise_for_status` functionality was implemented manually by checking the response status code.
4. **Populate Method**: Since `_get_addr` is now asynchronous, the `populate` method was also updated to be asynchronous and to use `await` when calling `_get_addr`.

### Modified Code
Here is the complete code after migrating to `treq`:

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

import treq
from twisted.internet.error import ConnectError

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

        self.headers = {
            'User-Agent': f'octodns/{octodns_version} octodns-ddns/{__VERSION__}'
        }

    async def _get_addr(self, _type):
        self.log.debug('_get_addr: type=%s', _type)
        try:
            resp = await treq.get(self.urls[_type], headers=self.headers)
            if resp.code != 200:
                raise Exception(
                    f'Failed to get IP address for type={_type}, status={resp.code}'
                )
            addr = (await resp.content()).decode('utf-8')
        except ConnectError:
            raise Exception(
                'Failed to get IP address for type={}'.format(_type)
            )
        self.log.info('_get_addr: type=%s is %s', _type, addr)
        return addr

    async def populate(self, zone, target=False, lenient=False):
        self.log.debug('populate: zone=%s', zone.name)
        before = len(zone.records)

        for _type in self.types:
            addr = await self._get_addr(_type)
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

### Key Notes
- The `treq` library is asynchronous, so the `async` keyword and `await` were introduced in the relevant methods.
- The `populate` method and `_get_addr` method are now asynchronous, which means any code calling these methods must also handle them as asynchronous functions.
- The `treq.get` method was used with headers passed explicitly, and the response content was decoded asynchronously using `await resp.content()`.
- Error handling was updated to check the response status code manually and to handle `ConnectError` from `twisted.internet.error`.

This migration ensures the code now uses `treq` while maintaining the original functionality and structure.