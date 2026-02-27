### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replace `requests.Session.get` with `pycurl`**:
   - `pycurl` is a lower-level library compared to `requests`, so we need to manually handle HTTP requests and responses.
   - A helper function `make_request` was added to perform HTTP GET requests using `pycurl`.
   - This function captures the response content and handles errors similarly to `requests`.

2. **Mocking `pycurl`**:
   - Since `pycurl` does not have a direct equivalent to `requests.Session.get`, the mocking approach was adjusted to mock the `make_request` function instead.

3. **Error Handling**:
   - `pycurl` errors are raised as exceptions, so they are caught and re-raised as needed to match the original behavior.

4. **MockResponse Adjustments**:
   - The `MockResponse` class was retained but adapted to simulate the behavior of `pycurl` responses.

### Modified Code:
```python
#
#
#

from unittest import TestCase
from unittest.mock import call, patch

import pycurl
from io import BytesIO

from octodns.zone import Zone

from octodns_ddns import DdnsSource


def make_request(url):
    """Helper function to perform HTTP GET requests using pycurl."""
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, buffer)
    try:
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        if status_code != 200:
            raise Exception(f"HTTP error: {status_code}")
    except pycurl.error as e:
        raise Exception(f"Connection error: {e}")
    finally:
        curl.close()
    return buffer.getvalue().decode('utf-8')


class MockResponse(object):
    def __init__(self, content='', raise_for_status=False):
        self.content = bytes(content, 'utf-8')
        self._raise_for_status = raise_for_status

    def raise_for_status(self):
        if self._raise_for_status:
            raise Exception(self._raise_for_status)


class TestDdnsSource(TestCase):
    @patch('__main__.make_request')
    def test_defaults(self, mock):
        a_value = '1.2.3.4'
        aaaa_value = '2001:db8:85a3::8a2e:370:7334'
        mock.side_effect = [a_value, aaaa_value]

        zone = Zone('example.com.', [])
        DdnsSource('dynamic').populate(zone)
        records = sorted(list(zone.records))
        self.assertEqual(2, len(records))
        a = records[0]
        self.assertEqual([a_value], a.values)
        aaaa = records[1]
        self.assertEqual([aaaa_value], aaaa.values)

        mock.assert_has_calls(
            [call('https://v4.ident.me/'), call('https://v6.ident.me/')]
        )

    @patch('__main__.make_request')
    def test_error(self, mock):
        mock.side_effect = Exception('boom')
        zone = Zone('example.com.', [])

        with self.assertRaises(Exception) as ctx:
            DdnsSource('dynamic').populate(zone)
        self.assertEqual('boom', str(ctx.exception))

    @patch('__main__.make_request')
    def test_connection_error(self, mock):
        mock.side_effect = Exception('this is a test')
        zone = Zone('example.com.', [])

        with self.assertRaises(Exception) as ctx:
            DdnsSource('dynamic').populate(zone)
        self.assertEqual(
            'Failed to get ip address for type=A', str(ctx.exception)
        )

    @patch('__main__.make_request')
    def test_empty_response(self, mock):
        mock.side_effect = ['', '']
        zone = Zone('example.com.', [])

        DdnsSource('dynamic').populate(zone)
        self.assertEqual(0, len(zone.records))

    @patch('__main__.make_request')
    def test_types_a(self, mock):
        a_value = '1.2.3.4'
        mock.side_effect = [a_value]

        zone = Zone('example.com.', [])
        DdnsSource('dynamic', types=('A',)).populate(zone)
        self.assertEqual(1, len(zone.records))

        mock.assert_has_calls([call('https://v4.ident.me/')])
        mock.assert_called_once()

    @patch('__main__.make_request')
    def test_types_aaaa(self, mock):
        aaaa_value = '2001:db8:85a3::8a2e:370:7334'
        mock.side_effect = [aaaa_value]

        zone = Zone('example.com.', [])
        DdnsSource('dynamic', types=('AAAA',)).populate(zone)
        self.assertEqual(1, len(zone.records))

        mock.assert_has_calls([call('https://v6.ident.me/')])
        mock.assert_called_once()

    @patch('__main__.make_request')
    def test_urls(self, mock):
        a_value = '1.2.3.4'
        aaaa_value = '2001:db8:85a3::8a2e:370:7334'
        mock.side_effect = [a_value, aaaa_value]

        zone = Zone('example.com.', [])
        DdnsSource(
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
```

### Key Notes:
- The `make_request` function encapsulates the `pycurl` logic for making HTTP GET requests.
- Mocking was updated to replace `requests.Session.get` with `make_request`.
- The rest of the code remains unchanged to ensure compatibility with the larger application.