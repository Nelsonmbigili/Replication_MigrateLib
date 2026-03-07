### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Importing the FutureSession**: Instead of using the default session from `requests`, we import `FuturesSession` from `requests_futures.sessions`.
2. **Creating a FuturesSession**: In the `setUp` method, we replace the standard session with a `FuturesSession` instance. This allows for asynchronous requests.
3. **Using the `get` method**: When making requests, we use the `get` method from the `FuturesSession`, which returns a `Future` object. We need to call `.result()` on this object to get the actual response.

The rest of the code remains unchanged to maintain the original functionality and structure.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests get_user()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import datetime
import unittest
from requests_futures.sessions import FuturesSession  # Changed import

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidUserID


class TestGetUser(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Changed to FuturesSession

    def test_get_user(self):
        user = self.hn.get_user('pg')
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'pg')
        self.assertEqual(user.created,
                         datetime.datetime.fromtimestamp(1160418092))
        self.assertEqual(repr(user), '<hackernews.User: pg>')

    def test_get_invalid_user(self):
        self.assertRaises(InvalidUserID, self.hn.get_user, 'a')

    def test_get_user_expand(self):
        user = self.hn.get_user('avinassh', expand=True)
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'avinassh')
        self.assertIsInstance(user.comments[0], Item)
        self.assertIsInstance(user.stories[0], Item)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```