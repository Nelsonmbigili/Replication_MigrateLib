### Explanation of Changes:
The original code uses the `requests` library for HTTP requests, but the migration requires using the `pycurl` library instead. The `pycurl` library operates at a lower level than `requests`, so the migration involves:
1. Replacing the `requests`-based HTTP calls in the `_get_sync` method with equivalent `pycurl` functionality.
2. Using `pycurl.Curl` to perform HTTP GET requests.
3. Capturing the response data using a `BytesIO` buffer since `pycurl` writes directly to a file-like object.
4. Handling errors by checking the HTTP response code and raising an `HTTPError` if necessary.

Below is the modified code with the necessary changes.

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import pycurl
from io import BytesIO
import json

from hackernews import HackerNews
from hackernews import HTTPError


class HackerNews:
    def _get_sync(self, url):
        """
        Perform a synchronous HTTP GET request using pycurl.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.setopt(pycurl.FOLLOWLOCATION, True)
        curl.setopt(pycurl.TIMEOUT, 10)

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            if status_code != 200:
                raise HTTPError(f"HTTP request failed with status code {status_code}")
        except pycurl.error as e:
            raise HTTPError(f"HTTP request failed: {e}")
        finally:
            curl.close()

        # Decode the response and parse JSON
        response_data = buffer.getvalue().decode('utf-8')
        return json.loads(response_data)


class TestGetSync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_sync(self):
        response = self.hn._get_sync(self.url)
        self.assertEqual(response['id'], 8863)
        self.assertEqual(response['by'], 'dhouston')

    def test_get_sync_error(self):
        self.assertRaises(HTTPError, self.hn._get_sync, self.err_url)

    def tearDown(self):
        pass  # No session to close when using pycurl


if __name__ == '__main__':
    unittest.main()
```

---

### Key Changes:
1. **Replaced `requests` with `pycurl`**:
   - The `_get_sync` method now uses `pycurl.Curl` to perform HTTP GET requests.
   - A `BytesIO` buffer is used to capture the response data since `pycurl` writes directly to a file-like object.

2. **Error Handling**:
   - Checked the HTTP response code using `curl.getinfo(pycurl.RESPONSE_CODE)`.
   - Raised an `HTTPError` if the response code is not 200 or if a `pycurl.error` occurs.

3. **JSON Parsing**:
   - Decoded the response data from the `BytesIO` buffer and parsed it using `json.loads`.

4. **Removed `session.close()`**:
   - Since `pycurl` does not use persistent sessions like `requests.Session`, the `tearDown` method no longer needs to close a session.

This ensures the code now uses `pycurl` for HTTP requests while maintaining the original functionality and structure.