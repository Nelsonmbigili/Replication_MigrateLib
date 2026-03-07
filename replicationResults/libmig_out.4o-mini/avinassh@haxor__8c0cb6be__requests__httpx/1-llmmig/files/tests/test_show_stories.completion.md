### Explanation of Changes

To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Session Management**: The `httpx` library uses `httpx.Client()` for session management instead of `requests.Session()`. This means that the way we create and close the session has changed.
2. **Closing the Session**: In `httpx`, the session is closed using the `__aexit__` method when using an asynchronous context manager, or by calling `close()` directly on the client instance. In this case, since the original code uses a synchronous context, we will directly call `close()` on the `httpx.Client()` instance.
3. **Import Statement**: The import statement for `httpx` needs to be added to replace `requests`.

The rest of the code remains unchanged to adhere to the guidelines provided.

### Modified Code

```python
#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import httpx  # Added import for httpx

from hackernews import HackerNews
from hackernews import Item


class TestShowStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = httpx.Client()  # Changed to use httpx.Client()

    def test_show_stories(self):
        show_stories = self.hn.show_stories(limit=10)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    def test_show_stories_raw(self):
        show_stories = self.hn.show_stories(raw=True)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    def tearDown(self):
        self.hn.session.close()  # No change needed here

if __name__ == '__main__':
    unittest.main()
```