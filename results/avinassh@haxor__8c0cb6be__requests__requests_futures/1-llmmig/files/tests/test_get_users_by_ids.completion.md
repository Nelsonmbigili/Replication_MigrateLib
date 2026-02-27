### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves using the `FuturesSession` class provided by `requests_futures` instead of the `Session` class from `requests`. The `FuturesSession` class allows for asynchronous HTTP requests, which is the main feature of `requests_futures`. 

In the provided code, the `HackerNews` class (not shown in the snippet) likely uses a `requests.Session` object for making HTTP requests. To migrate, we need to replace the `requests.Session` with `requests_futures.FuturesSession` in the `HackerNews` class. Additionally, the `close()` method for the session remains the same, so no changes are needed there.

Since the `HackerNews` class is not provided, I will assume it uses a `Session` object internally and modify the code accordingly to use `FuturesSession`.

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
from requests_futures.sessions import FuturesSession  # Updated import for requests_futures

from hackernews import HackerNews
from hackernews import User


class TestGetUsersByIDs(unittest.TestCase):

    def setUp(self):
        # Assuming HackerNews uses a session internally, we ensure it uses FuturesSession
        self.hn = HackerNews(session=FuturesSession())  # Pass FuturesSession to HackerNews

    def test_get_users_by_ids(self):
        users = self.hn.get_users_by_ids(['pg', 'tptacek', 'jacquesm'])
        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], User)

    def tearDown(self):
        self.hn.session.close()  # Close the FuturesSession

if __name__ == '__main__':
    unittest.main()
```

---

### Key Changes:
1. **Import `FuturesSession`**: Replaced the `requests` library's `Session` with `FuturesSession` from `requests_futures`.
   ```python
   from requests_futures.sessions import FuturesSession
   ```

2. **Use `FuturesSession` in `HackerNews`**: Updated the `setUp` method to initialize the `HackerNews` object with a `FuturesSession` instance. This assumes that the `HackerNews` class accepts a `session` parameter for dependency injection.
   ```python
   self.hn = HackerNews(session=FuturesSession())
   ```

3. **Session Cleanup**: The `tearDown` method remains unchanged because the `close()` method works the same way for both `Session` and `FuturesSession`.

---

### Assumptions:
- The `HackerNews` class has been implemented to accept a `session` parameter for dependency injection. If this is not the case, the `HackerNews` class itself would need to be modified to use `FuturesSession` internally.
- The rest of the code (e.g., `get_users_by_ids`) does not require changes because the migration only affects how HTTP requests are made, not the logic of the application.