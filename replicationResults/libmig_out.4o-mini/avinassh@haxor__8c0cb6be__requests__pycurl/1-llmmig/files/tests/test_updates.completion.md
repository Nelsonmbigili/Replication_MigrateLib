### Explanation of Changes
To migrate the code from using the `requests` library to using `pycurl`, the following changes were made:

1. **Importing `pycurl`**: The `requests` library was removed, and `pycurl` was imported instead.
2. **Session Management**: The `requests` session management was replaced with `pycurl`'s methods for handling HTTP requests.
3. **Making Requests**: The way to make HTTP requests changed significantly. Instead of using `requests.get()` or similar methods, `pycurl` requires setting options and performing the request using a `CURL` object.
4. **Handling Responses**: The response handling was adapted to read from a buffer since `pycurl` does not return the response directly like `requests`.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews


class TestUpdates(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_top_stories(self):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.hn.api_url + '/updates')  # Assuming api_url is defined in HackerNews
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        response_data = buffer.getvalue()
        updates = json.loads(response_data.decode('utf-8'))  # Assuming the response is JSON
        self.assertIsNotNone(updates)
        self.assertIsInstance(updates, dict)
        self.assertIsInstance(updates['profiles'], list)
        self.assertIsInstance(updates['items'], list)

    def tearDown(self):
        pass  # No session to close with pycurl

if __name__ == '__main__':
    unittest.main()
```

### Notes:
- The `self.hn.api_url` is assumed to be the endpoint for fetching updates. You may need to adjust this based on the actual implementation of the `HackerNews` class.
- The response is read into a `BytesIO` buffer, and then decoded and parsed as JSON.
- The `tearDown` method no longer needs to close a session, as `pycurl` does not maintain a session in the same way as `requests`.