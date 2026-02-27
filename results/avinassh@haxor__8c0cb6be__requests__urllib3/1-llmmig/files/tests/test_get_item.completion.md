### Explanation of Changes:
The original code uses the `requests` library for HTTP requests, but the migration requires switching to `urllib3`. The changes involve:
1. Replacing `requests`-specific methods (e.g., `requests.get`) with equivalent `urllib3` methods.
2. Managing the `urllib3.PoolManager` instance for making HTTP requests.
3. Ensuring proper cleanup of the `PoolManager` instance in the `tearDown` method.

The `HackerNews` class and its methods (`get_item`, etc.) are assumed to use `requests` internally. To migrate, the `HackerNews` class must be updated to use `urllib3`. Below is the modified code.

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests get_item()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
import urllib3
import json

from hackernews import Item, User
from hackernews import InvalidItemID


class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.http = urllib3.PoolManager()

    def get_item(self, item_id, expand=False):
        url = f"{self.BASE_URL}/item/{item_id}.json"
        response = self.http.request("GET", url)
        if response.status != 200:
            raise InvalidItemID(f"Invalid item ID: {item_id}")
        data = json.loads(response.data.decode("utf-8"))
        if not data:
            raise InvalidItemID(f"Invalid item ID: {item_id}")
        item = Item(data)
        if expand and "kids" in data:
            item.kids = [self.get_item(kid_id) for kid_id in data["kids"]]
        return item

    def close(self):
        self.http.clear()


class TestGetItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        item = self.hn.get_item(8863)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertEqual(item.by, "dhouston")
        self.assertEqual(
            repr(item),
            ('<hackernews.Item: 8863 - My YC app: '
                'Dropbox - Throw away your USB drive>')
        )

    def test_invalid_item(self):
        self.assertRaises(InvalidItemID, self.hn.get_item, 0)

    def test_get_item_expand(self):
        item = self.hn.get_item(8863, expand=True)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertIsInstance(item.by, User)
        self.assertIsInstance(item.kids[0], Item)

    def tearDown(self):
        self.hn.close()


if __name__ == '__main__':
    unittest.main()
```

---

### Key Changes:
1. **`HackerNews` Class**:
   - Replaced `requests` with `urllib3.PoolManager` for HTTP requests.
   - Used `self.http.request("GET", url)` to fetch data.
   - Decoded the response using `response.data.decode("utf-8")`.
   - Added a `close` method to clear the `PoolManager` instance.

2. **`tearDown` Method**:
   - Updated to call `self.hn.close()` to ensure proper cleanup of the `urllib3.PoolManager` instance.

3. **Error Handling**:
   - Checked `response.status` for HTTP status codes instead of relying on `requests` exceptions.

These changes ensure the code now uses `urllib3` version 2.3.0 instead of `requests`.