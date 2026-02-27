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
from io import BytesIO

import pycurl

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

        # Initialize pycurl.Curl object
        self._curl = pycurl.Curl()
        self._curl.setopt(
            pycurl.USERAGENT,
            f'octodns/{octodns_version} octodns-ddns/{__VERSION__}',
        )

    def _get_addr(self, _type):
        self.log.debug('_get_addr: type=%s', _type)
        url = self.urls[_type]
        buffer = BytesIO()

        try:
            # Set URL and output buffer
            self._curl.setopt(pycurl.URL, url)
            self._curl.setopt(pycurl.WRITEDATA, buffer)

            # Perform the request
            self._curl.perform()

            # Check HTTP response code
            http_code = self._curl.getinfo(pycurl.RESPONSE_CODE)
            if http_code != 200:
                raise Exception(
                    f'Failed to get ip address for type={_type}, HTTP {http_code}'
                )

            # Decode the response
            addr = buffer.getvalue().decode('utf-8')
            self.log.info('_get_addr: type=%s is %s', _type, addr)
            return addr

        except pycurl.error as e:
            raise Exception(
                f'Failed to get ip address for type={_type}, error: {e}'
            )

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
