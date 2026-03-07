### Explanation of Changes
To migrate from the `requests` library to the `requests_futures` library, the primary change involves how HTTP requests are made. The `requests_futures` library allows for asynchronous requests by using a `FuturesSession` instead of the standard `Session`. This change requires modifying the way the session is created and how the requests are executed. Specifically, we will replace the `requests.Session()` with `FuturesSession()` and adjust the method of making requests to accommodate the future object returned by `requests_futures`.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession
from hackernews import HackerNews


class TestUpdates(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Change to FuturesSession

    def test_top_stories(self):
        updates_future = self.hn.updates()  # This will return a future
        updates = updates_future.result()  # Get the result from the future
        self.assertIsNotNone(updates)
        self.assertIsInstance(updates, dict)
        self.assertIsInstance(updates['profiles'], list)
        self.assertIsInstance(updates['items'], list)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
``` 

In this modified code, the `self.hn.session` is now an instance of `FuturesSession`, and the result of the `updates()` method is obtained by calling `.result()` on the future object. This allows the code to work asynchronously while maintaining the original structure and functionality.