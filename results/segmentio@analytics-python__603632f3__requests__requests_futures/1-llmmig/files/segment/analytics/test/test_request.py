from datetime import datetime, date
import unittest
import json
from requests_futures.sessions import FuturesSession

from segment.analytics.request import post, DatetimeSerializer


class TestRequests(unittest.TestCase):

    def test_valid_request(self):
        session = FuturesSession()
        future = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }], session=session)
        res = future.result()  # Wait for the response
        self.assertEqual(res.status_code, 200)

    def test_invalid_request_error(self):
        session = FuturesSession()
        self.assertRaises(Exception, post, 'testsecret',
                          'https://api.segment.io', False, '[{]', session=session)

    def test_invalid_host(self):
        session = FuturesSession()
        self.assertRaises(Exception, post, 'testsecret',
                          'api.segment.io/', batch=[], session=session)

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
        session = FuturesSession()
        future = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }], timeout=15, session=session)
        res = future.result()  # Wait for the response
        self.assertEqual(res.status_code, 200)

    def test_should_timeout(self):
        session = FuturesSession()
        with self.assertRaises(Exception):  # Adjusted to handle FuturesSession exceptions
            future = post('testsecret', batch=[{
                'userId': 'userId',
                'event': 'python event',
                'type': 'track'
            }], timeout=0.0001, session=session)
            future.result()  # This will raise the timeout exception

    def test_proxies(self):
        session = FuturesSession()
        future = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track',
            'proxies': '203.243.63.16:80'
        }], session=session)
        res = future.result()  # Wait for the response
        self.assertEqual(res.status_code, 200)
