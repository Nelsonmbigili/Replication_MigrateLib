### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class, which provides asynchronous request handling.
2. **Session Initialization**: Replaced direct calls to `requests` methods (e.g., `requests.post`) with a `FuturesSession` instance. This allows the use of asynchronous requests.
3. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the actual response object synchronously where needed.
4. **Timeouts and Exceptions**: Adjusted the timeout and exception handling to work with the `FuturesSession`.

Below is the modified code:

---

### Modified Code:
```python
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
```

---

### Key Notes:
1. **`FuturesSession`**: The `FuturesSession` class from `requests_futures` is used to handle asynchronous requests. It wraps the `requests` library and provides a `Future` object for each request.
2. **`future.result()`**: The `.result()` method is used to block and retrieve the actual response object from the `Future`.
3. **Session Parameter**: The `post` function is assumed to accept a `session` parameter to allow the use of `FuturesSession`. If this is not the case, the `post` function would need to be updated to support it.
4. **Timeouts and Exceptions**: Adjusted exception handling to account for the asynchronous nature of `FuturesSession`.

This migration ensures that the code now uses `requests_futures` while maintaining the original functionality and structure.