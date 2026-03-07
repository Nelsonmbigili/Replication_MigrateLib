### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the primary change involves how HTTP requests are made. The `requests_futures` library allows for asynchronous requests by using a `FuturesSession` instead of the standard `Session`. This means that instead of directly calling methods on the `session` object, we will use the `FuturesSession` to send requests and handle the responses asynchronously.

In the modified code, I will:
1. Import `FuturesSession` from `requests_futures.sessions`.
2. Replace the standard session with a `FuturesSession` in the `HackerNews` class (assuming it uses `self.session` for requests).
3. Ensure that the code remains functionally the same while adapting to the asynchronous nature of `requests_futures`.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests get_max_item()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
from requests_futures.sessions import FuturesSession  # Importing FuturesSession

from hackernews import HackerNews
from hackernews import Item


class TestGetMaxItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Using FuturesSession instead of requests.Session

    def test_get_max_item(self):
        max_item_id = self.hn.get_max_item()
        self.assertIsInstance(max_item_id, int)

    def test_get_max_item_expand(self):
        max_item = self.hn.get_max_item(expand=True)
        self.assertIsInstance(max_item, Item)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
``` 

In this modified code, the only changes made were to import `FuturesSession` and to instantiate it in the `setUp` method of the test class. The rest of the code remains unchanged to maintain the original functionality and structure.