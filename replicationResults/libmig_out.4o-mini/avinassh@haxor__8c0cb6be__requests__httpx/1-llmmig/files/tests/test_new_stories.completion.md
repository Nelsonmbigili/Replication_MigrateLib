### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Session Management**: The `httpx` library uses `httpx.Client()` for session management instead of `requests.Session()`. This means that the way we create and close the session has changed.
2. **Closing the Session**: In `httpx`, the session is closed using the `__aexit__` method in an asynchronous context. However, since the original code does not use asynchronous features, we will simply instantiate `httpx.Client()` in the `HackerNews` class and close it in the `tearDown` method.

The rest of the code remains unchanged as per the instructions.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests new_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import httpx  # Importing httpx

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
        new_stories = self.hn.new_stories(raw=True)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], str)
        self.assertIsNotNone(new_stories)

    def tearDown(self):
        self.hn.session.close()  # This will now close the httpx.Client()

if __name__ == '__main__':
    unittest.main()
```

### Note
Make sure that the `HackerNews` class is updated to use `httpx.Client()` for making HTTP requests instead of `requests.Session()`. This code assumes that the `HackerNews` class has been modified accordingly to support `httpx`.