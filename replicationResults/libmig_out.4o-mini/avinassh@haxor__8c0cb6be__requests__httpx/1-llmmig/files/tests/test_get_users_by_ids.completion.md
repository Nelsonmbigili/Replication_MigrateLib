### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Session Management**: The `httpx` library uses `httpx.Client()` for session management instead of `requests.Session()`. This means that the way we create and close the session has changed.
2. **Asynchronous Support**: While the original code does not use asynchronous features, `httpx` supports both synchronous and asynchronous requests. In this case, we will continue using the synchronous approach.
3. **Import Statement**: The import statement for `httpx` is added, and the `requests` import is removed.

The rest of the code remains unchanged to adhere to the guidelines provided.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import httpx  # Importing httpx instead of requests

from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = httpx.Client()  # Using httpx.Client() for session management

    def test_get_users_by_ids(self):
        users = self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        self.hn.session.close()  # Closing the httpx.Client() session

if __name__ == '__main__':
    unittest.main()
```