### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the following changes were made:
1. **Importing `FuturesSession`**: The `requests_futures` library provides `FuturesSession`, which is used for asynchronous HTTP requests. This replaces the synchronous `requests.Session` used in the original code.
2. **Updating the `HackerNews` class**: The `HackerNews` class (assumed to be part of the `hackernews` module) likely uses `requests.Session` internally. To migrate, the `HackerNews` class should use `FuturesSession` instead. Since the `HackerNews` class is not provided in the original code, I assume it uses a `session` attribute for HTTP requests, and I updated the `tearDown` method to close the `FuturesSession`.

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest

from hackernews import HackerNews
from hackernews import Item
from requests_futures.sessions import FuturesSession  # Import FuturesSession


class TestShowStories(unittest.TestCase):

    def setUp(self):
        # Initialize HackerNews instance (assumes it uses FuturesSession internally)
        self.hn = HackerNews()

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
        # Close the FuturesSession
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

### Key Notes:
- The migration assumes that the `HackerNews` class uses a `session` attribute for HTTP requests. If this is not the case, the `HackerNews` class itself would need to be updated to use `FuturesSession` instead of `requests.Session`.
- The `tearDown` method ensures that the `FuturesSession` is properly closed after the tests are run.
- No other parts of the code were modified, as per the instructions.