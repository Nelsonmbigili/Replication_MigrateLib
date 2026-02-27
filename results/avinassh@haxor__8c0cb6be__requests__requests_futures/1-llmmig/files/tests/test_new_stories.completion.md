### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves using the `FuturesSession` class provided by `requests_futures` instead of the `Session` class from `requests`. The `FuturesSession` class allows for asynchronous HTTP requests, which is the main feature of `requests_futures`.

In the provided code:
1. The `HackerNews` class (assumed to be part of the `hackernews` module) likely uses a `requests.Session` object for making HTTP requests. To migrate, we need to replace this with a `FuturesSession` object from `requests_futures`.
2. The `tearDown` method closes the session. This remains unchanged, as `FuturesSession` also has a `close` method.

The changes are minimal and only involve ensuring that the `HackerNews` class uses `FuturesSession` instead of `Session`.

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests new_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession  # Import FuturesSession
from hackernews import HackerNews
from hackernews import Item


class TestNewStories(unittest.TestCase):

    def setUp(self):
        # Assuming HackerNews accepts a session object, we pass a FuturesSession instance
        self.hn = HackerNews(session=FuturesSession())

    def test_new_stories(self):
        new_stories = self.hn.new_stories(limit=10)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], Item)
        self.assertIsNotNone(new_stories)

    def test_new_stories_raw(self):
        new_stories = self.hn.new_stories(raw=True)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], str)
        self.assertIsNotNone(new_stories)

    def tearDown(self):
        self.hn.session.close()  # Close the FuturesSession

if __name__ == '__main__':
    unittest.main()
```

---

### Key Changes:
1. **Import FuturesSession**: Added `from requests_futures.sessions import FuturesSession` to import the `FuturesSession` class.
2. **Use FuturesSession in HackerNews**: Updated the `setUp` method to initialize `HackerNews` with a `FuturesSession` instance. This assumes that the `HackerNews` class accepts a session object as an argument (a common pattern in libraries that use `requests`).
3. **Session Closing**: The `tearDown` method remains unchanged, as `FuturesSession` also provides a `close` method to clean up resources.

No other changes were made to the code, as per the instructions.