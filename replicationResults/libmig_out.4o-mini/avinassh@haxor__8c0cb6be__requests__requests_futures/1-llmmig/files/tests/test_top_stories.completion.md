### Explanation of Changes
To migrate from the `requests` library to the `requests_futures` library, the primary change involves how HTTP requests are made. The `requests_futures` library allows for asynchronous requests by using a `FuturesSession` instead of the standard `Session`. This means that instead of directly calling methods on the session, we will use the `FuturesSession` to send requests and handle the responses asynchronously.

In the modified code, I will:
1. Import `FuturesSession` from `requests_futures.sessions`.
2. Replace the standard session with a `FuturesSession` in the `HackerNews` class (assuming it uses a session internally).
3. Ensure that the requests made in the `top_stories` method are compatible with the `FuturesSession`.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests top_stories()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
from requests_futures.sessions import FuturesSession  # Import FuturesSession

from hackernews import HackerNews
from hackernews import Item


class TestTopStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Use FuturesSession instead of requests.Session

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
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
``` 

This code now uses `requests_futures` to handle HTTP requests asynchronously while maintaining the original structure and functionality of the application.