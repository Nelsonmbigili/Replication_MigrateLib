### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Session Management**: The `requests` library uses a session object to manage connections, while `urllib3` requires a different approach. Instead of using `self.hn.session`, we will create an instance of `urllib3.PoolManager` to handle HTTP connections.
2. **Making Requests**: The way requests are made differs between the two libraries. In `requests`, you typically use methods like `get()` or `post()`, while in `urllib3`, you use the `urlopen()` method of the `PoolManager`.
3. **Response Handling**: The response object from `urllib3` is different from that of `requests`. We need to read the response data differently.

The following code reflects these changes while maintaining the original structure and naming conventions.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests new_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import urllib3
import json

from hackernews import HackerNews
from hackernews import Item


class TestNewStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.http = urllib3.PoolManager()

    def test_new_stories(self):
        new_stories = self.hn.new_stories(limit=10)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], Item)
        self.assertIsNotNone(new_stories)

    def test_new_stories_raw(self):
        new_stories = self.hn.new_stories(raw=True)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], str)
        self.assertIsNotNone(new_stories)

    def tearDown(self):
        pass  # No explicit close needed for urllib3.PoolManager

if __name__ == '__main__':
    unittest.main()
```

### Additional Notes
- The `tearDown` method no longer needs to close a session, as `urllib3.PoolManager` manages connections differently and does not require explicit closure.
- The actual implementation of the `new_stories` method in the `HackerNews` class would need to be updated to use `self.hn.http.urlopen()` for making HTTP requests, but that part of the code is not provided here.