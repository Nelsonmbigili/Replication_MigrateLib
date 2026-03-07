### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`.
2. **Creating a PoolManager**: Instead of using a session object as in `requests`, `urllib3` requires creating a `PoolManager` to handle connections.
3. **Making GET Requests**: The method for making GET requests changed from `requests.get()` to `urllib3.PoolManager().request()`.
4. **Handling Response**: The response handling was adjusted to access the data from the `urllib3` response object, which requires decoding the JSON data from the response body.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import urllib3
import json

from hackernews import HackerNews


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'
        self.http = urllib3.PoolManager()

    def test_get_async(self):
        response = self.http.request('GET', self.url)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['id'], 8863)
        self.assertEqual(data['by'], 'dhouston')

    def test_get_async_error(self):
        response = self.http.request('GET', self.err_url)
        self.assertEqual(response.status, 404)

    def tearDown(self):
        pass  # No session to close in urllib3

if __name__ == '__main__':
    unittest.main()
``` 

### Note
- The `tearDown` method was modified to remove the session closing since `urllib3` does not maintain a session in the same way as `requests`.