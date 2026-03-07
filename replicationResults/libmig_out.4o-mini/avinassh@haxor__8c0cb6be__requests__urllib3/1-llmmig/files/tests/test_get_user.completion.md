### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Session Management**: The `requests` library uses a session object to manage connections, while `urllib3` requires a different approach. We create a `PoolManager` instance in `urllib3` to handle connections.
2. **HTTP Requests**: The way to make HTTP requests changes from `requests.get()` to `urllib3.PoolManager().request()`. The parameters for the request method also differ slightly.
3. **Response Handling**: The response object from `urllib3` is different from that of `requests`. We need to access the response data using `response.data` and decode it if necessary.
4. **Error Handling**: The way exceptions are raised and handled may differ, so we ensure that the migration maintains the same error handling logic.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests get_user()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import datetime
import unittest
import urllib3
import json

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidUserID


class TestGetUser(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.http = urllib3.PoolManager()

    def test_get_user(self):
        response = self.hn.http.request('GET', f'https://hacker-news.firebaseio.com/v0/user/pg.json')
        user_data = json.loads(response.data.decode('utf-8'))
        user = self.hn.get_user(user_data)
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'pg')
        self.assertEqual(user.created,
                         datetime.datetime.fromtimestamp(1160418092))
        self.assertEqual(repr(user), '<hackernews.User: pg>')

    def test_get_invalid_user(self):
        self.assertRaises(InvalidUserID, self.hn.get_user, 'a')

    def test_get_user_expand(self):
        response = self.hn.http.request('GET', f'https://hacker-news.firebaseio.com/v0/user/avinassh.json')
        user_data = json.loads(response.data.decode('utf-8'))
        user = self.hn.get_user(user_data, expand=True)
        self.assertIsInstance(user, User)
        self.assertEqual(user.user_id, 'avinassh')
        self.assertIsInstance(user.comments[0], Item)
        self.assertIsInstance(user.stories[0], Item)

    def tearDown(self):
        pass  # No need to close the PoolManager

if __name__ == '__main__':
    unittest.main()
```

### Notes:
- The `HackerNews` class is assumed to be modified to handle the `user_data` received from the `urllib3` response.
- The `tearDown` method no longer needs to close a session, as `urllib3` manages connections differently.