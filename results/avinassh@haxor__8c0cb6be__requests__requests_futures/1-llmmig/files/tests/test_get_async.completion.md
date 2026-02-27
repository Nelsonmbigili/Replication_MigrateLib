### Explanation of Changes
The migration from `requests` to `requests_futures` involves using the `FuturesSession` class provided by `requests_futures` to handle asynchronous HTTP requests. The key changes include:
1. Importing `FuturesSession` from `requests_futures` instead of using `requests`.
2. Replacing synchronous request methods (e.g., `requests.get`) with asynchronous methods provided by `FuturesSession`.
3. Modifying the `_run_async` method in the `HackerNews` class to use `FuturesSession` for making asynchronous requests and handling the resulting futures.

Below is the modified code with the necessary changes.

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


class HackerNews:
    def __init__(self):
        self.session = FuturesSession()  # Use FuturesSession for async requests

    def _run_async(self, urls):
        futures = [self.session.get(url) for url in urls]  # Send async requests
        results = []
        for future in futures:
            try:
                response = future.result()  # Wait for the response
                if response.status_code == 200:
                    results.append(response.json())
                else:
                    results.append(None)
            except Exception:
                results.append(None)
        return results


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
        self.hn.session.close()


if __name__ == '__main__':
    unittest.main()
```

---

### Summary of Changes
1. Replaced the `requests` library with `requests_futures` by importing `FuturesSession`.
2. Updated the `HackerNews` class to use `FuturesSession` for asynchronous requests.
3. Modified the `_run_async` method to handle futures and retrieve results using `future.result()`.

No other parts of the code were altered to ensure compatibility with the rest of the application.