#
#
#

from unittest import TestCase
from unittest.mock import call, patch, AsyncMock

from aiohttp import ClientError

from octodns.zone import Zone

from octodns_ddns import DdnsSource


class MockResponse(object):
    def __init__(self, content='', raise_for_status=False):
        self.content = bytes(content, 'utf-8')
        self._raise_for_status = raise_for_status

    async def read(self):
        return self.content

    async def raise_for_status(self):
        if self._raise_for_status:
            raise Exception(self._raise_for_status)


class TestDdnsSource(TestCase):
    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    async def test_defaults(self, mock):
        a_value = '1.2.3.4'
        aaaa_value = '2001:db8:85a3::8a2e:370:7334'
        mock.side_effect = [
            MockResponse(a_value),
            MockResponse(aaaa_value),
        ]

        zone = Zone('example.com.', [])
        await DdnsSource('dynamic').populate(zone)
        records = sorted(list(zone.records))
        self.assertEqual(2, len(records))
        a = records[0]
        self.assertEqual([a_value], a.values)
        aaaa = records[1]
        self.assertEqual([aaaa_value], aaaa.values)

        mock.assert_has_calls(
            [call('https://v4.ident.me/'), call('https://v6.ident.me/')]
        )

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    async def test_error(self, mock):
        mock.side_effect = [MockResponse(raise_for_status='boom')]
        zone = Zone('example.com.', [])

        with self.assertRaises(Exception) as ctx:
            await DdnsSource('dynamic').populate(zone)
        self.assertEqual('boom', str(ctx.exception))

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    async def test_connection_error(self, mock):
        mock.side_effect = [ClientError('this is a test')]
        zone = Zone('example.com.', [])

        with self.assertRaises(Exception) as ctx:
            await DdnsSource('dynamic').populate(zone)
        self.assertEqual(
            'Failed to get ip address for type=A', str(ctx.exception)
        )

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    async def test_empty_response(self, mock):
        mock.side_effect = [MockResponse(content=''), MockResponse(content='')]
        zone = Zone('example.com.', [])

        await DdnsSource('dynamic').populate(zone)
        self.assertEqual(0, len(zone.records))

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    async def test_types_a(self, mock):
        a_value = '1.2.3.4'
        mock.side_effect = [MockResponse(a_value)]

        zone = Zone('example.com.', [])
        await DdnsSource('dynamic', types=('A',)).populate(zone)
        self.assertEqual(1, len(zone.records))

        mock.assert_has_calls([call('https://v4.ident.me/')])
        mock.assert_called_once()

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    async def test_types_aaaa(self, mock):
        aaaa_value = '2001:db8:85a3::8a2e:370:7334'
        mock.side_effect = [MockResponse(aaaa_value)]

        zone = Zone('example.com.', [])
        await DdnsSource('dynamic', types=('AAAA',)).populate(zone)
        self.assertEqual(1, len(zone.records))

        mock.assert_has_calls([call('https://v6.ident.me/')])
        mock.assert_called_once()

    @patch('aiohttp.ClientSession.get', new_callable=AsyncMock)
    async def test_urls(self, mock):
        a_value = '1.2.3.4'
        aaaa_value = '2001:db8:85a3::8a2e:370:7334'
        mock.side_effect = [
            MockResponse(a_value),
            MockResponse(aaaa_value),
        ]

        zone = Zone('example.com.', [])
        await DdnsSource(
            'dynamic',
            urls={'A': 'https://foo.bar/v4', 'AAAA': 'https://foo.bar/v6'},
        ).populate(zone)
        records = sorted(list(zone.records))
        self.assertEqual(2, len(records))
        a = records[0]
        self.assertEqual([a_value], a.values)
        aaaa = records[1]
        self.assertEqual([aaaa_value], aaaa.values)

        mock.assert_has_calls(
            [call('https://foo.bar/v4'), call('https://foo.bar/v6')]
        )
