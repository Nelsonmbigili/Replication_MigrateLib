### Explanation of Changes:
To migrate from `requests` to `aiohttp`, the following changes were made:
1. **Session Management**: `aiohttp` uses an asynchronous `ClientSession` for making HTTP requests. The `HackerNews` class (assumed to be part of the `hackernews` module) likely uses a `requests.Session`. This needs to be replaced with an `aiohttp.ClientSession`.
2. **Asynchronous Methods**: `aiohttp` is asynchronous, so methods that make HTTP requests (e.g., `get_last`) need to be awaited. This requires marking the test methods as `async` and using `await` where necessary.
3. **Event Loop**: Since `unittest` does not natively support asynchronous test methods, we use `asyncio.run()` to execute the asynchronous test methods.
4. **Session Cleanup**: The `tearDown` method is updated to close the `aiohttp.ClientSession` asynchronously using `await`.

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests get_all()

@author john keck
@email robertjkeck
"""

import unittest
import asyncio

from hackernews import HackerNews
from hackernews import Item


class TestGetLast(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        async def async_test():
            items = await self.hn.get_last(5)
            self.assertIsInstance(items, list)
            self.assertEqual(len(items), 5)
            self.assertIsInstance(items[0], Item)

        asyncio.run(async_test())

    def tearDown(self):
        async def async_teardown():
            await self.hn.session.close()

        asyncio.run(async_teardown())


if __name__ == '__main__':
    unittest.main()
```

### Key Notes:
- The `HackerNews` class and its `get_last` method are assumed to have been updated to use `aiohttp` and to be asynchronous. If they are not yet updated, you will need to modify them accordingly.
- The `asyncio.run()` function is used to execute asynchronous code within the synchronous `unittest` framework.
- The `tearDown` method ensures that the `aiohttp.ClientSession` is properly closed to avoid resource leaks.