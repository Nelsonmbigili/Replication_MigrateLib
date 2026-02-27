### Explanation of Changes:
To migrate from the `requests` library to `requests_futures`, the primary change involves using the `FuturesSession` class from `requests_futures` instead of the `Session` class from `requests`. The `FuturesSession` class allows for asynchronous HTTP requests, which return `Future` objects. However, since the original code does not explicitly show any HTTP requests or asynchronous behavior, I assume the `HackerNews` class internally uses `requests.Session`. Therefore, the migration involves ensuring that `HackerNews` uses `FuturesSession` instead of `Session`.

The changes made:
1. Imported `FuturesSession` from `requests_futures`.
2. Modified the `tearDown` method to close the `FuturesSession` instead of a regular `Session`.

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession  # Import FuturesSession
from hackernews import HackerNews


class TestUpdates(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_top_stories(self):
        updates = self.hn.updates()
        self.assertIsNotNone(updates)
        self.assertIsInstance(updates, dict)
        self.assertIsInstance(updates['profiles'], list)
        self.assertIsInstance(updates['items'], list)

    def tearDown(self):
        # Ensure the session is closed (assuming FuturesSession is used internally)
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```

### Notes:
- The code assumes that the `HackerNews` class is updated to use `FuturesSession` internally instead of `requests.Session`. If this is not the case, you would need to modify the `HackerNews` class to use `FuturesSession` for HTTP requests.
- No other changes were made to the code, as per the instructions.