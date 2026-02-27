### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Importing `FuturesSession`**: The `requests_futures` library provides `FuturesSession` for asynchronous HTTP requests. This replaces the synchronous `requests.Session` used in the original code.
2. **Updating the `HackerNews` class**: The `HackerNews` class (assumed to be part of the `hackernews` module) likely uses `requests.Session`. This needs to be updated to use `FuturesSession` instead.
3. **Closing the session**: The `tearDown` method in the test class closes the session. This remains unchanged, as `FuturesSession` also has a `close` method.

Since the `HackerNews` class is not provided in the original code, I will assume it uses `requests.Session` internally and modify it to use `FuturesSession`. Below is the modified code.

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck
"""

import unittest
from requests_futures.sessions import FuturesSession  # Updated import for FuturesSession
from hackernews import HackerNews
from hackernews import Item


# Assuming the HackerNews class is defined in the hackernews module
# and uses requests.Session internally. Modify it to use FuturesSession.
class HackerNews:
    def __init__(self):
        self.session = FuturesSession()  # Use FuturesSession instead of requests.Session

    def get_items_by_ids(self, ids, item_type=None):
        # Example implementation of an asynchronous request
        futures = [self.session.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json") for id in ids]
        responses = [future.result() for future in futures]  # Wait for all futures to complete
        items = [response.json() for response in responses if response.status_code == 200]

        if item_type:
            items = [item for item in items if item.get('type') == item_type]

        return [Item(**item) for item in items]


class TestGetItemsByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_items_by_ids(self):
        items = self.hn.get_items_by_ids([1, 2, 3])
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 3)
        self.assertIsInstance(items[0], Item)

    def test_get_items_by_ids_filtered(self):
        items = self.hn.get_items_by_ids(
            [i for i in range(1, 50)],
            item_type='story'
        )
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 37)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        self.hn.session.close()


if __name__ == '__main__':
    unittest.main()
```

---

### Summary of Changes:
1. Replaced `requests.Session` with `FuturesSession` in the `HackerNews` class.
2. Updated the `get_items_by_ids` method in `HackerNews` to handle asynchronous requests using `FuturesSession`.
3. Ensured the `tearDown` method still closes the session properly.

This migration ensures the code now uses `requests_futures` for asynchronous HTTP requests while maintaining the original functionality and structure.