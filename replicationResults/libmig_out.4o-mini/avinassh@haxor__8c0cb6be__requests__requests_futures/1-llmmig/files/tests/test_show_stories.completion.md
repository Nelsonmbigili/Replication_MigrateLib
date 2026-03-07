### Explanation of Changes
To migrate from the `requests` library to the `requests_futures` library, the primary change involves how HTTP requests are made. The `requests_futures` library allows for asynchronous requests by using a `FuturesSession` instead of the standard `Session`. This means that instead of directly calling methods on the session to get responses, we will use the `FuturesSession` to send requests and then retrieve the results from the future object.

In the modified code, I will:
1. Import `FuturesSession` from `requests_futures.sessions`.
2. Replace the standard session with a `FuturesSession` in the `HackerNews` class (assuming it uses `requests` internally).
3. Adjust the way responses are handled to accommodate the future object returned by `FuturesSession`.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession  # Importing FuturesSession

from hackernews import HackerNews
from hackernews import Item


class TestShowStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Using FuturesSession instead of requests.Session

    def test_show_stories(self):
        future = self.hn.show_stories(limit=10)  # Assuming show_stories returns a future
        show_stories = future.result()  # Getting the result from the future
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    def test_show_stories_raw(self):
        future = self.hn.show_stories(raw=True)  # Assuming show_stories returns a future
        show_stories = future.result()  # Getting the result from the future
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

In this modified code, I have made the necessary adjustments to utilize `requests_futures` while keeping the overall structure and logic intact. The `show_stories` method in the `HackerNews` class is assumed to return a future object, which is then resolved using the `.result()` method.