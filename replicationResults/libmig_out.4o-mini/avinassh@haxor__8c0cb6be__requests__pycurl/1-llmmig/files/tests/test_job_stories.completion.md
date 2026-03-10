### Explanation of Changes

To migrate the code from using the `requests` library to using `pycurl`, the following changes were made:

1. **Importing `pycurl`**: The `requests` library was removed, and `pycurl` was imported instead.
2. **Session Management**: The `requests` session management was replaced with `pycurl`'s methods for handling HTTP requests.
3. **Making Requests**: The way requests are made and responses are handled changed significantly. `pycurl` requires setting options for the request and handling the response differently compared to `requests`.
4. **Data Handling**: The response data is captured using a callback function in `pycurl`, which is different from the straightforward response object in `requests`.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests job_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import Item


class TestJobStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_job_stories(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/jobstories.json?limit=10')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        job_stories = self.hn.parse_response(buffer.getvalue())
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], Item)
        self.assertIsNotNone(job_stories)

    def test_job_stories_raw(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/jobstories.json?raw=true')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        job_stories = self.hn.parse_response_raw(buffer.getvalue())
        self.assertIsInstance(job_stories, list)
        self.assertIsInstance(job_stories[0], str)
        self.assertIsNotNone(job_stories)

    def tearDown(self):
        pass  # No session to close in pycurl

if __name__ == '__main__':
    unittest.main()
```

### Notes:
- The `parse_response` and `parse_response_raw` methods are assumed to be part of the `HackerNews` class to handle the response data appropriately after fetching it with `pycurl`. You may need to implement these methods if they do not already exist.
- The `tearDown` method was modified to remove the session close call since `pycurl` does not maintain a session in the same way as `requests`.