### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Importing the FutureSession**: Instead of using the standard `requests` session, we import `FuturesSession` from `requests_futures.sessions`.
2. **Creating a FuturesSession**: In the `setUp` method, we replace the standard session with a `FuturesSession` instance. This allows for asynchronous requests.
3. **Handling Asynchronous Calls**: The `get_users_by_ids` method should be modified to use the `FuturesSession` for making requests. This typically involves calling the `session.get()` method and then using the `result()` method to retrieve the response.

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
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Changed to FuturesSession

    def test_get_users_by_ids(self):
        users_future = self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])  # Assuming this method is updated to handle futures
        users = users_future.result()  # Get the result from the future
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

### Note
The `get_users_by_ids` method in the `HackerNews` class should be updated to handle the asynchronous nature of `FuturesSession`. This typically involves returning a future object instead of the actual response directly. If this method is not already designed to work with futures, additional modifications will be necessary in the `HackerNews` class.