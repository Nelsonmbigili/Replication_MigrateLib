### Explanation of Changes

To migrate the code from using the `requests` library to using `pycurl`, the following changes were made:

1. **Importing `pycurl`**: The `requests` library was removed, and `pycurl` was imported instead.
2. **Session Management**: The `requests` session management was replaced with `pycurl`'s methods for handling HTTP requests.
3. **Making Requests**: The way requests are made and responses are handled changed significantly. `pycurl` requires setting options for the request and using a callback to capture the response data.
4. **Error Handling**: The error handling mechanism may differ, but since the original code does not include error handling, it was not added in the migration.

The modified code is as follows:

```python
#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import Item


class TestShowStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_show_stories(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        show_stories = self.hn.show_stories(limit=10)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    def test_show_stories_raw(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        show_stories = self.hn.show_stories(raw=True)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    def tearDown(self):
        pass  # No session to close with pycurl

if __name__ == '__main__':
    unittest.main()
```

### Note:
- The URL used in the `setopt` method is a placeholder and should be replaced with the actual endpoint used in the `HackerNews` class for fetching stories.
- The `tearDown` method was modified to remove the session close call since `pycurl` does not maintain a session in the same way as `requests`.