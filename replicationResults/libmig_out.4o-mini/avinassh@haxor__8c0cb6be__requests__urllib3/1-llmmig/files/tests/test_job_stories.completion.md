### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Session Management**: The `requests` library uses a session object for managing connections, while `urllib3` requires a different approach. We create a `PoolManager` instance from `urllib3` to handle connections.
2. **HTTP Requests**: The way to make HTTP requests changes from `requests.get()` to `urllib3.PoolManager().request()`. The parameters for the request method are also slightly different.
3. **Response Handling**: The response object from `urllib3` does not have the same attributes as the one from `requests`. We need to access the response data using `response.data` and decode it if necessary.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests job_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import urllib3
import json

from hackernews import HackerNews
from hackernews import Item


class TestJobStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.http = urllib3.PoolManager()

    def test_job_stories(self):
        response = self.hn.http.request('GET', 'https://hacker-news.firebaseio.com/v0/jobstories.json?print=pretty&limit=10')
        job_stories = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], Item)
        self.assertIsNotNone(job_stories)

    def test_job_stories_raw(self):
        response = self.hn.http.request('GET', 'https://hacker-news.firebaseio.com/v0/jobstories.json?print=pretty&raw=true')
        job_stories = response.data.decode('utf-8').splitlines()
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], str)
        self.assertIsNotNone(job_stories)

    def tearDown(self):
        pass  # No need to close the PoolManager

if __name__ == '__main__':
    unittest.main()
```

### Note
- The `tearDown` method no longer needs to close a session since `urllib3.PoolManager` does not require explicit closure like `requests.Session()`.