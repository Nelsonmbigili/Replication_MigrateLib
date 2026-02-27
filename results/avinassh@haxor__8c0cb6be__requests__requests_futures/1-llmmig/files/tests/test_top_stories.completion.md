### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves using the `FuturesSession` class provided by `requests_futures` instead of the `Session` class from `requests`. The `FuturesSession` class allows for asynchronous HTTP requests using Python's `concurrent.futures`. 

In the provided code, the `HackerNews` class (presumably part of the `hackernews` module) likely uses a `requests.Session` object for making HTTP requests. To migrate, we need to ensure that the `HackerNews` class uses a `FuturesSession` object instead. Since the `HackerNews` class is not provided, I will assume it uses a `session` attribute for HTTP requests, and I will modify the `tearDown` method to close the `FuturesSession` properly.

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests top_stories()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
from requests_futures.sessions import FuturesSession  # Import FuturesSession
from hackernews import HackerNews
from hackernews import Item


class TestTopStories(unittest.TestCase):

    def setUp(self):
        # Assuming HackerNews uses a session attribute for HTTP requests
        self.hn = HackerNews()

    def test_top_stories(self):
        top_stories = self.hn.top_stories(limit=10)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], Item)
        self.assertIsNotNone(top_stories)

    def test_top_stories_raw(self):
        top_stories = self.hn.top_stories(raw=True)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], str)
        self.assertIsNotNone(top_stories)

    def tearDown(self):
        # Close the FuturesSession properly
        if hasattr(self.hn, 'session') and isinstance(self.hn.session, FuturesSession):
            self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

### Key Changes:
1. **Import `FuturesSession`**: Added `from requests_futures.sessions import FuturesSession` to use the `FuturesSession` class.
2. **Close `FuturesSession` in `tearDown`**: Updated the `tearDown` method to check if the `session` attribute of the `HackerNews` instance is a `FuturesSession` and close it properly.

### Assumptions:
- The `HackerNews` class uses a `session` attribute for HTTP requests, which is common in libraries that use `requests`.
- The migration to `requests_futures` does not require changes to the `HackerNews` class itself, as it should work seamlessly with `FuturesSession` if it was designed to use `requests.Session`.

No other changes were made to the code, as per the instructions.