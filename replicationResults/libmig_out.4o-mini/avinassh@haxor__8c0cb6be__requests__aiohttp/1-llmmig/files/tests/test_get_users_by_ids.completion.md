### Explanation of Changes
To migrate the code from using the `requests` library to the `aiohttp` library, the following changes were made:

1. **Asynchronous Functions**: The `get_users_by_ids` method needs to be modified to be asynchronous, as `aiohttp` is designed for asynchronous operations.
2. **Session Management**: Instead of using `self.hn.session.close()`, we will use an `async with` statement to manage the session lifecycle.
3. **Awaiting Requests**: Any HTTP requests made with `aiohttp` must be awaited, which requires the use of the `await` keyword.
4. **Event Loop**: The test runner needs to be adjusted to run the asynchronous test methods.

### Modified Code
Here is the modified code using `aiohttp`:

```python
#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import asyncio

from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.hn = HackerNews()

    async def test_get_users_by_ids(self):
        users = await self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    async def asyncTearDown(self):
        await self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

### Notes
- The `TestGetUsersByIDs` class now inherits from `unittest.IsolatedAsyncioTestCase` to support asynchronous test methods.
- The `setUp` and `tearDown` methods have been replaced with `asyncSetUp` and `asyncTearDown` to accommodate the asynchronous nature of `aiohttp`.
- The `get_users_by_ids` method is awaited to ensure the asynchronous call is properly handled.