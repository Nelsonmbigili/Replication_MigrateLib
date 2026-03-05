### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The `requests` library was replaced with `requests_futures.sessions` to utilize the `FuturesSession` class, which allows for asynchronous requests.
2. **Session Initialization**: Instead of directly using the `post` method from the `requests` library, a `FuturesSession` object was created to handle the requests asynchronously.
3. **Handling Responses**: The response from the `post` method is now accessed through the `Future` object returned by the `FuturesSession`. The `result()` method is called on the `Future` object to get the actual response.

Here is the modified code:

```python
from datetime import datetime, date
import unittest
import json
from requests_futures.sessions import FuturesSession

from segment.analytics.request import post, DatetimeSerializer

class TestRequests(unittest.TestCase):
    def setUp(self):
        self.session = FuturesSession()

    def test_valid_request(self):
        future = self.session.post('https://api.segment.io', json={
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }, headers={'Authorization': 'Bearer testsecret'})
        res = future.result()
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
        future = self.session.post('https://api.segment.io', json={
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }, headers={'Authorization': 'Bearer testsecret'}, timeout=15)
        res = future.result()
        self.assertEqual(res.status_code, 200)

    def test_should_timeout(self):
        with self.assertRaises(requests.ReadTimeout):
            future = self.session.post('https://api.segment.io', json={
                'userId': 'userId',
                'event': 'python event',
                'type': 'track'
            }, headers={'Authorization': 'Bearer testsecret'}, timeout=0.0001)
            future.result()

    def test_proxies(self):
        future = self.session.post('https://api.segment.io', json={
            'userId': 'userId',
            'event': 'python event',
            'type': 'track',
            'proxies': '203.243.63.16:80'
        }, headers={'Authorization': 'Bearer testsecret'})
        res = future.result()
        self.assertEqual(res.status_code, 200)
```

### Note
- The `post` function from the `segment.analytics.request` module is assumed to be compatible with the changes made. If it internally uses `requests`, it may need to be modified to work with `FuturesSession` as shown in the test cases.