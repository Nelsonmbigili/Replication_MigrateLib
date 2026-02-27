### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import `FuturesSession`**: The `requests_futures` library provides asynchronous functionality through the `FuturesSession` class. This replaces the synchronous `requests.Session` used in the original code.
2. **Update the `HackerNews` class**: The `_get_sync` method in the `HackerNews` class likely uses `requests` for synchronous HTTP requests. Since `requests_futures` is designed for asynchronous requests, the `_get_sync` method is updated to use `FuturesSession` for making requests. However, since the method is named `_get_sync`, we ensure the response is resolved synchronously by calling `.result()` on the future object.
3. **Close the `FuturesSession`**: The `tearDown` method is updated to close the `FuturesSession` instead of the `requests.Session`.

Below is the modified code.

---

### Modified Code
```python
#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck
"""

import unittest
from requests_futures.sessions import FuturesSession  # Updated import
from hackernews import HackerNews
from hackernews import HTTPError


class HackerNews:
    def __init__(self):
        self.session = FuturesSession()  # Use FuturesSession instead of requests.Session

    def _get_sync(self, url):
        # Make the request asynchronously but wait for the result to keep it synchronous
        future = self.session.get(url)
        response = future.result()  # Wait for the response
        if response.status_code != 200:
            raise HTTPError(f"HTTP error: {response.status_code}")
        return response.json()


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
        self.hn.session.close()  # Close the FuturesSession

if __name__ == '__main__':
    unittest.main()
```

---

### Summary of Changes
1. Replaced `requests.Session` with `FuturesSession` from `requests_futures`.
2. Updated the `_get_sync` method to use `FuturesSession.get()` and resolve the future synchronously with `.result()`.
3. Ensured the `FuturesSession` is properly closed in the `tearDown` method.