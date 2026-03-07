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
Tests job_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession  # Importing FuturesSession

from hackernews import HackerNews
from hackernews import Item


class TestJobStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Using FuturesSession instead of requests.Session

    def test_job_stories(self):
        job_stories_future = self.hn.job_stories(limit=10)
        job_stories = job_stories_future.result()  # Getting the result from the future
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], Item)
        self.assertIsNotNone(job_stories)

    def test_job_stories_raw(self):
        job_stories_future = self.hn.job_stories(raw=True)
        job_stories = job_stories_future.result()  # Getting the result from the future
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], str)
        self.assertIsNotNone(job_stories)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
``` 

In this modified code, the `FuturesSession` is used to allow for asynchronous requests, and the results are accessed using the `.result()` method on the future object returned by the `job_stories` method.