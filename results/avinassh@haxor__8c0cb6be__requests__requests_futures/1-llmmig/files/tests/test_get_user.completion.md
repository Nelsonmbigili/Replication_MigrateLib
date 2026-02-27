### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves replacing synchronous HTTP requests with asynchronous requests using `requests_futures`. The `requests_futures` library provides a `FuturesSession` class, which allows requests to be executed asynchronously. 

In the provided code, the `HackerNews` class likely uses `requests` for making HTTP requests. To migrate, we need to:
1. Replace the `requests.Session` object in the `HackerNews` class with a `requests_futures.FuturesSession` object.
2. Ensure that any HTTP requests made by the `HackerNews` class are compatible with the asynchronous nature of `requests_futures`.
3. Update the `tearDown` method to close the `FuturesSession` instead of a `requests.Session`.

Since the `HackerNews` class is not provided in the code snippet, I will assume it uses a `requests.Session` object internally and modify the `tearDown` method accordingly.

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests get_user()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import datetime
import unittest

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidUserID


class TestGetUser(unittest.TestCase):

    def setUp(self):
        # Initialize the HackerNews instance
        self.hn = HackerNews()

    def test_get_user(self):
        # Test fetching a valid user
        user = self.hn.get_user('pg')
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'pg')
        self.assertEqual(user.created,
                         datetime.datetime.fromtimestamp(1160418092))
        self.assertEqual(repr(user), '<hackernews.User: pg>')

    def test_get_invalid_user(self):
        # Test fetching an invalid user
        self.assertRaises(InvalidUserID, self.hn.get_user, 'a')

    def test_get_user_expand(self):
        # Test fetching a user with expanded data
        user = self.hn.get_user('avinassh', expand=True)
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'avinassh')
        self.assertIsInstance(user.comments[0], Item)
        self.assertIsInstance(user.stories[0], Item)

    def tearDown(self):
        # Close the FuturesSession instead of a regular Session
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

---

### Key Assumptions:
1. The `HackerNews` class uses a `requests.Session` object internally, which has been replaced with a `requests_futures.FuturesSession` object.
2. The `get_user` method in the `HackerNews` class is compatible with asynchronous requests or has been updated to handle them.
3. The `tearDown` method now closes the `FuturesSession` object instead of a `requests.Session`.

If the `HackerNews` class or its methods require further modifications to support `requests_futures`, those changes would need to be made in the `HackerNews` implementation, which is not provided in the original code snippet.