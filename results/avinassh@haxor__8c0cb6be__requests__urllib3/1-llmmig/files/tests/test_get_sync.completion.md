### Explanation of Changes:
The original code uses the `requests` library for HTTP requests. To migrate to `urllib3`, the following changes were made:
1. Replaced the `requests` session with an `urllib3.PoolManager` instance for managing HTTP connections.
2. Updated the `_get_sync` method in the `HackerNews` class to use `urllib3` for making HTTP requests.
3. Handled HTTP errors using `urllib3.exceptions.HTTPError` and `urllib3.response.HTTPResponse` instead of `requests` exceptions.
4. Ensured proper cleanup of the `PoolManager` instance in the `tearDown` method.

Below is the modified code:

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck
"""

import unittest
import json
import urllib3
from urllib3.exceptions import HTTPError


class HackerNews:
    def __init__(self):
        self.session = urllib3.PoolManager()

    def _get_sync(self, url):
        try:
            response = self.session.request('GET', url)
            if response.status != 200:
                raise HTTPError(f"HTTP error: {response.status}")
            return json.loads(response.data.decode('utf-8'))
        except HTTPError as e:
            raise HTTPError(f"Failed to fetch data: {e}")


class TestGetSync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_sync(self):
        response = self.hn._get_sync(self.url)
        self.assertEqual(response['id'], 8863)
        self.assertEqual(response['by'], 'dhouston')

    def test_get_sync_error(self):
        self.assertRaises(HTTPError, self.hn._get_sync, self.err_url)

    def tearDown(self):
        self.hn.session.clear()  # Properly close the PoolManager


if __name__ == '__main__':
    unittest.main()
```

---

### Key Changes:
1. **`urllib3.PoolManager`**: Replaced the `requests.Session` with `urllib3.PoolManager` for connection pooling.
2. **`session.request`**: Used `self.session.request('GET', url)` to make HTTP GET requests.
3. **Error Handling**: Used `urllib3.exceptions.HTTPError` to handle HTTP errors and raised exceptions when the status code was not 200.
4. **Response Decoding**: Used `response.data.decode('utf-8')` to decode the response body from bytes to a string, then parsed it with `json.loads`.
5. **Cleanup**: Used `self.hn.session.clear()` in the `tearDown` method to release resources held by the `PoolManager`.

This ensures the code now uses `urllib3` version 2.3.0 while maintaining the original functionality.