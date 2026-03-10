### Explanation of Changes
To migrate the code from using the `requests` library to using `pycurl`, the following changes were made:

1. **Importing `pycurl`**: The `requests` library was removed, and `pycurl` was imported instead.
2. **Session Management**: The `requests` session management was replaced with `pycurl`'s method of handling HTTP requests. This involves creating a `pycurl.Curl` object for each request.
3. **Making Requests**: The way requests are made and responses are handled changed significantly. `pycurl` requires setting options for the request and then performing the request, which is different from the simpler interface provided by `requests`.
4. **Response Handling**: The response from `pycurl` is captured in a buffer, which is then converted to a string for further processing.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests new_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import Item


class TestNewStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_new_stories(self):
        new_stories = self.hn.new_stories(limit=10)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], Item)
        self.assertIsNotNone(new_stories)

    def test_new_stories_raw(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        body = buffer.getvalue().decode('utf-8')
        new_stories = eval(body)  # Assuming the response is a JSON array of story IDs
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], str)
        self.assertIsNotNone(new_stories)

    def tearDown(self):
        pass  # No session to close with pycurl

if __name__ == '__main__':
    unittest.main()
```

### Note
- The `new_stories` method in the `HackerNews` class is assumed to be modified to use `pycurl` as well, as the original code does not show its implementation. The example provided in `test_new_stories_raw` demonstrates how to use `pycurl` to fetch data directly.