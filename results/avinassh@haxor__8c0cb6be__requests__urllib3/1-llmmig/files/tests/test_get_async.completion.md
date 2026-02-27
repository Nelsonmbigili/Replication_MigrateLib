### Explanation of Changes:
The original code uses the `requests` library for HTTP requests. To migrate to `urllib3`, the following changes were made:
1. Replaced `requests`-specific methods with equivalent `urllib3` methods.
2. Created an `urllib3.PoolManager` instance to manage HTTP connections (similar to `requests.Session`).
3. Updated the `_run_async` method in the `HackerNews` class to use `urllib3` for making HTTP GET requests.
4. Handled HTTP responses using `urllib3`'s `response.data` and `json.loads` to parse JSON data, as `urllib3` does not automatically decode JSON like `requests`.

Below is the modified code:

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjke
"""

import unittest
import urllib3
import json

from hackernews import HackerNews


class HackerNews:
    def __init__(self):
        self.session = urllib3.PoolManager()

    def _run_async(self, urls):
        responses = []
        for url in urls:
            try:
                response = self.session.request('GET', url)
                if response.status == 200:
                    responses.append(json.loads(response.data.decode('utf-8')))
                else:
                    responses.append(None)
            except Exception:
                responses.append(None)
        return responses


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_async(self):
        response = self.hn._run_async([self.url])
        self.assertEqual(response[0]['id'], 8863)
        self.assertEqual(response[0]['by'], 'dhouston')

    def test_get_async_error(self):
        response = self.hn._run_async([self.err_url])
        self.assertEqual(response, [None])

    def tearDown(self):
        self.hn.session.clear()  # Close the PoolManager


if __name__ == '__main__':
    unittest.main()
```

---

### Key Changes:
1. **`urllib3.PoolManager`**:
   - Replaced `requests.Session` with `urllib3.PoolManager` for managing HTTP connections.
   - Added `self.session = urllib3.PoolManager()` in the `HackerNews` class.

2. **HTTP GET Requests**:
   - Replaced `requests.get(url)` with `self.session.request('GET', url)`.

3. **Response Handling**:
   - Used `response.data.decode('utf-8')` to decode the response body from bytes to a string.
   - Used `json.loads()` to parse the JSON response, as `urllib3` does not automatically parse JSON.

4. **Error Handling**:
   - Wrapped the request in a `try-except` block to handle exceptions (e.g., connection errors).

5. **Session Cleanup**:
   - Used `self.hn.session.clear()` in the `tearDown` method to clean up the `PoolManager` instance.

This ensures the code now uses `urllib3` while maintaining the original functionality.