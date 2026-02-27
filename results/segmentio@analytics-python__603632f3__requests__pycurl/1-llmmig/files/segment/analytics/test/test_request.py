from datetime import datetime, date
import unittest
import json
import pycurl
from io import BytesIO

from segment.analytics.request import DatetimeSerializer


def post(secret, url='https://api.segment.io', batch=None, timeout=None, proxies=None):
    """
    Replaces the `requests.post` functionality with `pycurl`.
    """
    if batch is None:
        batch = []

    # Prepare the data payload
    data = json.dumps({
        'secret': secret,
        'batch': batch
    })

    # Buffer to capture the response
    response_buffer = BytesIO()

    # Initialize pycurl
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.POST, 1)
    curl.setopt(pycurl.POSTFIELDS, data)
    curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
    curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])

    # Set timeout if provided
    if timeout is not None:
        curl.setopt(pycurl.TIMEOUT_MS, int(timeout * 1000))

    # Set proxy if provided
    if proxies:
        curl.setopt(pycurl.PROXY, proxies)

    try:
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        response_body = response_buffer.getvalue().decode('utf-8')
        curl.close()

        # Simulate a response object for compatibility
        class Response:
            def __init__(self, status_code, text):
                self.status_code = status_code
                self.text = text

        return Response(status_code, response_body)

    except pycurl.error as e:
        curl.close()
        raise Exception(f"Request failed: {e}")


class TestRequests(unittest.TestCase):

    def test_valid_request(self):
        res = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }])
        self.assertEqual(res.status_code, 200)

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
        self.assertEqual(res.status_code, 200)

    def test_should_timeout(self):
        with self.assertRaises(Exception):  # pycurl raises a generic exception for timeouts
            post('testsecret', batch=[{
                'userId': 'userId',
                'event': 'python event',
                'type': 'track'
            }], timeout=0.0001)

    def test_proxies(self):
        res = post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }], proxies='203.243.63.16:80')
        self.assertEqual(res.status_code, 200)
