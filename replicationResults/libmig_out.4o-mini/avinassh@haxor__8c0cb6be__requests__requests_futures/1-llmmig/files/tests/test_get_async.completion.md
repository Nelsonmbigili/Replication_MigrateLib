### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Importing the FutureSession**: Instead of using the standard `requests` session, we import `FuturesSession` from `requests_futures.sessions`.
2. **Creating a FutureSession**: In the `setUp` method, we replace the standard session with a `FuturesSession` instance.
3. **Using the `get` method**: The `_run_async` method is replaced with the `get` method of the `FuturesSession`, which allows for asynchronous requests. The response is accessed using the `result()` method of the future object.

### Modified Code
```python
#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
from requests_futures.sessions import FuturesSession
from hackernews import HackerNews


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Use FuturesSession for async requests
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_async(self):
        future = self.hn.session.get(self.url)  # Use get method of FuturesSession
        response = future.result()  # Get the result of the future
        self.assertEqual(response.json()['id'], 8863)
        self.assertEqual(response.json()['by'], 'dhouston')

    def test_get_async_error(self):
        future = self.hn.session.get(self.err_url)  # Use get method of FuturesSession
        response = future.result()  # Get the result of the future
        self.assertEqual(response, None)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
```