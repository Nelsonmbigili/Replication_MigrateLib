### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The `requests` library is replaced with `requests_futures.sessions`. This allows us to use the `FuturesSession` class, which provides asynchronous capabilities.
2. **Session Initialization**: Instead of using the standard `requests.Session()`, we now use `FuturesSession()` to create a session that can handle requests asynchronously.
3. **Method Calls**: The method calls remain the same, but they will now return a `Future` object instead of the actual response. We need to call `.result()` on the future to get the response.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests ask_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession  # Changed import

from hackernews import HackerNews
from hackernews import Item


class TestAskStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Changed to FuturesSession

    def test_ask_stories(self):
        future = self.hn.ask_stories(limit=10)
        ask_stories = future.result()  # Get the result from the future
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], Item)
        self.assertIsNotNone(ask_stories)

    def test_ask_stories_raw(self):
        future = self.hn.ask_stories(raw=True)
        ask_stories = future.result()  # Get the result from the future
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], str)
        self.assertIsNotNone(ask_stories)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
``` 

This code now uses `requests_futures` to handle asynchronous requests while maintaining the original structure and functionality.