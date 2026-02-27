from datetime import datetime, date
import unittest
import json
import urllib3

from segment.analytics.request import post, DatetimeSerializer


class TestRequests(unittest.TestCase):

    def test_valid_request(self):
        res = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }])
        self.assertEqual(res.status, 200)

    def test_invalid_request_error(self):
        self.assertRaises(Exception, post, 'testsecret',
                          'https://api.segment.io', False, '[{]')

    def test_invalid_host(self):
        self.assertRaises(Exception, post, 'testsecret',
                          'api.segment.io/', batch=[])

    def test_datetime_serialization(self):
        data = {'created': datetime(2012, 3, 4, 5, 6, 7, 891011)}
        result = json.dumps(data, cls=DatetimeSerializer)
        self.assertEqual(result, '{"created": "2012-03-04T05:06:07.891011"}')

    def test_date_serialization(self):
        today = date.today()
        data = {'created': today}
        result = json.dumps(data, cls=DatetimeSerializer)
        expected = '{"created": "%s"}' % today.isoformat()
        self.assertEqual(result, expected)

    def test_should_not_timeout(self):
        res = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }], timeout=15)
        self.assertEqual(res.status, 200)

    def test_should_timeout(self):
        with self.assertRaises(urllib3.exceptions.ReadTimeoutError):
            post('testsecret', batch=[{
                'userId': 'userId',
                'event': 'python event',
                'type': 'track'
            }], timeout=0.0001)

    def test_proxies(self):
        res = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track',
            'proxies': '203.243.63.16:80'
        }])
        self.assertEqual(res.status, 200)


# Updated `post` function to use `urllib3`
def post(secret, url='https://api.segment.io', batch=None, timeout=None, proxies=None):
    http = urllib3.PoolManager()

    if proxies:
        http = urllib3.ProxyManager(f'http://{proxies}')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {secret}'
    }

    try:
        encoded_data = json.dumps(batch).encode('utf-8')
        response = http.request(
            'POST',
            url,
            body=encoded_data,
            headers=headers,
            timeout=timeout
        )
        return response
    except urllib3.exceptions.HTTPError as e:
        raise Exception(f"HTTP request failed: {e}")
