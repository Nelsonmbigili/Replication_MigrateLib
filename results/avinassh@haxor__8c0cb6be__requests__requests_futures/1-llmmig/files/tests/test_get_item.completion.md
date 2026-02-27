### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves using the `FuturesSession` class provided by `requests_futures` instead of the `Session` class from `requests`. The `FuturesSession` class allows for asynchronous HTTP requests, which return `Future` objects. These `Future` objects can be resolved to get the actual response.

In the provided code, the `HackerNews` class likely uses a `requests.Session` object for making HTTP requests. To migrate, we need to replace the `Session` object with a `FuturesSession` object. Additionally, if the `HackerNews` class uses synchronous requests, we need to ensure that the `Future` objects returned by `FuturesSession` are resolved to maintain the synchronous behavior.

Here is the modified code:

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

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidItemID
from requests_futures.sessions import FuturesSession  # Import FuturesSession


class TestGetItem(unittest.TestCase):

    def setUp(self):
        # Replace the session in HackerNews with a FuturesSession
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Use FuturesSession for async requests

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
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

---

### Key Changes:
1. **Import `FuturesSession`**: Added `from requests_futures.sessions import FuturesSession` to import the `FuturesSession` class from the `requests_futures` library.
2. **Replace `Session` with `FuturesSession`**: In the `setUp` method, replaced the `requests.Session` object in the `HackerNews` class with a `FuturesSession` object. This ensures that all HTTP requests made by the `HackerNews` class use `requests_futures`.
3. **No Other Changes**: The rest of the code remains unchanged, as the migration only affects how HTTP requests are made. The synchronous behavior of the tests is preserved by resolving the `Future` objects internally in the `HackerNews` class (assumed to be handled there).

This ensures the code is migrated to use `requests_futures` while maintaining the original functionality and coding style.