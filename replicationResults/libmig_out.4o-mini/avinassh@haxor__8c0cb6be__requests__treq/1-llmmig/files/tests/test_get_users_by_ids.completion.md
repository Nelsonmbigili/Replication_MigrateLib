### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Session Management**: The `requests` library uses a session object that is typically created with `requests.Session()`. In `treq`, session management is handled differently, and we don't need to explicitly close a session as `treq` manages it internally.
2. **HTTP Requests**: The way to make HTTP requests remains similar, but we will use `treq.get()` instead of `requests.get()`. The parameters and response handling will also be adjusted to fit `treq`'s API.

The modified code reflects these changes while keeping the original structure intact.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import treq

from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_users_by_ids(self):
        users = self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        pass  # No need to close session in treq

if __name__ == '__main__':
    unittest.main()
``` 

Note: The actual implementation of `get_users_by_ids` in the `HackerNews` class would need to be updated to use `treq` for making HTTP requests, but since the instruction was to only modify the provided code, I have not included those changes.