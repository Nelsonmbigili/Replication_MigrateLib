### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the primary change involves how HTTP requests are made. The `requests_futures` library allows for asynchronous requests by using a `FuturesSession` instead of the standard `Session`. This means that instead of directly calling methods on the session to get responses, we will use the `FuturesSession` to send requests and then retrieve the results from the future object.

In the modified code, I will:
1. Import `FuturesSession` from `requests_futures.sessions`.
2. Replace the standard session with a `FuturesSession`.
3. Adjust the way responses are handled to accommodate the asynchronous nature of `requests_futures`.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests new_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession  # Changed import

from hackernews import HackerNews
from hackernews import Item


class TestNewStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Changed to FuturesSession

    def test_new_stories(self):
        future = self.hn.new_stories(limit=10)  # Assuming this method is adjusted to return a future
        new_stories = future.result()  # Get the result from the future
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], Item)
        self.assertIsNotNone(new_stories)

    def test_new_stories_raw(self):
        future = self.hn.new_stories(raw=True)  # Assuming this method is adjusted to return a future
        new_stories = future.result()  # Get the result from the future
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], str)
        self.assertIsNotNone(new_stories)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

### Note
The code assumes that the `new_stories` method in the `HackerNews` class has been modified to return a future object instead of directly returning the result. If this method has not been adjusted, further changes will be necessary in the `HackerNews` class to support asynchronous requests.