### Explanation of Changes:
The original code does not directly use the `requests` library, but it likely relies on the `requests` library indirectly through the `HackerNews` class. To migrate to `treq`, we need to ensure that the `HackerNews` class and its methods (e.g., `get_users_by_ids`) use `treq` for HTTP requests instead of `requests`. Since the provided code does not include the implementation of the `HackerNews` class, I will assume that it uses `requests` for HTTP requests and modify it accordingly.

The key changes involve:
1. Replacing `requests` with `treq` for making HTTP requests.
2. Since `treq` is asynchronous, we need to use `async def` for methods that make HTTP requests and use `await` for `treq` calls.
3. Updating the test case to handle asynchronous methods using `asyncio.run`.

Below is the modified code:

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjkeck
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

---

### Key Notes:
1. **`IsolatedAsyncioTestCase`**: Since `treq` is asynchronous, the test case is updated to use `unittest.IsolatedAsyncioTestCase`, which supports asynchronous test methods.
2. **`asyncSetUp` and `asyncTearDown`**: These methods are used to set up and tear down asynchronous resources.
3. **`await`**: The `get_users_by_ids` method is assumed to be asynchronous, so it is called with `await`.

If the `HackerNews` class implementation is available, it would also need to be updated to use `treq` for HTTP requests. Let me know if you need assistance with that part as well!