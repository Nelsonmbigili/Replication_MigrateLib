### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves using the `FuturesSession` class provided by `requests_futures` instead of the `Session` class from `requests`. The `FuturesSession` class allows for asynchronous HTTP requests using Python's `concurrent.futures`. 

In the provided code, the `HackerNews` class (presumably part of the `hackernews` module) likely uses a `requests.Session` object for making HTTP requests. To migrate, we need to ensure that the `HackerNews` class uses a `FuturesSession` object instead. This change is made in the `setUp` and `tearDown` methods of the test class, where the session is initialized and closed.

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests get_max_item()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
from requests_futures.sessions import FuturesSession  # Import FuturesSession
from hackernews import HackerNews
from hackernews import Item


class TestGetMaxItem(unittest.TestCase):

    def setUp(self):
        # Replace the session in HackerNews with a FuturesSession
        self.hn = HackerNews()
        self.hn.session = FuturesSession()

    def test_get_max_item(self):
        max_item_id = self.hn.get_max_item()
        self.assertIsInstance(max_item_id, int)

    def test_get_max_item_expand(self):
        max_item = self.hn.get_max_item(expand=True)
        self.assertIsInstance(max_item, Item)

    def tearDown(self):
        # Close the FuturesSession
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

### Summary of Changes:
1. Imported `FuturesSession` from `requests_futures.sessions`.
2. Replaced the `requests.Session` object in the `HackerNews` class with a `FuturesSession` object in the `setUp` method.
3. Ensured the `FuturesSession` is properly closed in the `tearDown` method.

These changes ensure that the code now uses `requests_futures` for asynchronous HTTP requests while maintaining the original functionality and structure of the test suite.