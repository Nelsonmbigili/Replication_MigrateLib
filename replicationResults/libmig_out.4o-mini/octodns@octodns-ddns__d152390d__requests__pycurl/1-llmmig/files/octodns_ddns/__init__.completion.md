### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, the following changes were made:

1. **Importing PyCurl**: The `requests` library was replaced with `pycurl`. The `Session` object from `requests` was removed, and instead, a `pycurl.Curl` object was created for making HTTP requests.
  
2. **Making Requests**: The `get` method from `requests` was replaced with the `setopt` method of the `pycurl.Curl` object to configure the request options. The URL is set using `CURLOPT_URL`, and the response is captured using a `BytesIO` object.

3. **Error Handling**: The `ConnectionError` from `requests` was replaced with a generic exception handling for `pycurl` errors.

4. **Response Handling**: The response content is read from the `BytesIO` object instead of directly from the response object as done in `requests`.

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
import pycurl
from io import BytesIO

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

    def _get_addr(self, _type):
        self.log.debug('_get_addr: type=%s', _type)
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, self.urls[_type])
        curl.setopt(curl.WRITEDATA, buffer)
        curl.setopt(curl.FOLLOWLOCATION, True)

        try:
            curl.perform()
        except pycurl.error as e:
            raise Exception(
                'Failed to get ip address for type={}'.format(_type)
            ) from e
        finally:
            curl.close()

        addr = buffer.getvalue().decode('utf-8')
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