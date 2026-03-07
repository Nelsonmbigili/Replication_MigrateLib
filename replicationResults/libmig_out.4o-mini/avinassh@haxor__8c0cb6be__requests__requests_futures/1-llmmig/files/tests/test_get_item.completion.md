### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Importing the FutureSession**: Instead of using the default session from `requests`, we import `FuturesSession` from `requests_futures.sessions`.
2. **Creating a FutureSession**: In the `setUp` method, we replace the standard session with a `FuturesSession` instance. This allows for asynchronous requests.
3. **Updating the `get_item` Method**: The `get_item` method needs to be modified to use the `FuturesSession` for making requests. This typically involves calling the `get` method on the `FuturesSession` instance, which returns a future object.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests get_item()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
from requests_futures.sessions import FuturesSession  # Changed import

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidItemID


class TestGetItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Changed to FuturesSession

    def test_get_item(self):
        future = self.hn.get_item(8863)  # Assuming get_item uses session to make a request
        item = future.result()  # Get the result from the future
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
        future = self.hn.get_item(8863, expand=True)  # Assuming get_item uses session to make a request
        item = future.result()  # Get the result from the future
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertIsInstance(item.by, User)
        self.assertIsInstance(item.kids[0], Item)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

### Note
The `get_item` method in the `HackerNews` class is assumed to be modified to return a future object when using `FuturesSession`. If it is not currently designed to do so, you will need to adjust that method accordingly to ensure it works with the `FuturesSession`.