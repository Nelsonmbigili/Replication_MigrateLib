### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Session Management**: The `requests` library uses `requests.Session()` for session management, while `httpx` uses `httpx.Client()`. The session is created in the `HackerNews` class, and the `close()` method is called in the `tearDown()` method.
2. **HTTP Methods**: The methods for making HTTP requests (like `get`, `post`, etc.) are similar in both libraries, but they are called on the `httpx.Client()` instance instead of a `requests.Session()` instance.
3. **Error Handling**: The way exceptions are raised and handled may differ slightly, but in this case, the existing error handling with `InvalidUserID` remains unchanged.

The following code reflects these changes while keeping the original structure intact.

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

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidUserID
import httpx  # Import httpx

class TestGetUser(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

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
        self.hn.session.close()  # This will now close the httpx.Client()

if __name__ == '__main__':
    unittest.main()
``` 

Note: The actual implementation of the `HackerNews` class and its methods (like `get_user`) would need to be updated to use `httpx.Client()` instead of `requests.Session()`, but those changes are not shown here as per your instructions.