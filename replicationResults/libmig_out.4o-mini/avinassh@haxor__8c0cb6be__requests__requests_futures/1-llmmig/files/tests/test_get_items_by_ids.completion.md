### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The `requests` library is replaced with `requests_futures.sessions`. This allows us to use the `FuturesSession` class, which provides asynchronous capabilities.
2. **Session Initialization**: Instead of using the standard `requests.Session()`, we now create an instance of `FuturesSession()` from the `requests_futures` library. This enables the ability to make non-blocking requests.
3. **Handling Requests**: The method for making requests remains the same, but we will need to ensure that we handle the future response correctly. This typically involves calling `.result()` on the future object to get the actual response.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
from requests_futures.sessions import FuturesSession  # Changed import

from hackernews import HackerNews
from hackernews import Item


class TestGetItemsByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Changed to FuturesSession

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

### Note
The actual implementation of the `get_items_by_ids` method in the `HackerNews` class may need to be adjusted to handle the asynchronous nature of `requests_futures`, specifically by calling `.result()` on the future response. However, since the instructions specify not to alter the original coding style or functionality beyond the migration, those changes are not included here.