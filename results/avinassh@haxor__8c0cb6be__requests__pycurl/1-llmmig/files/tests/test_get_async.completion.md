### Explanation of Changes:
The original code uses the `requests` library for HTTP requests, but the migration requires replacing it with the `pycurl` library. Since `pycurl` operates at a lower level than `requests`, the migration involves:
1. Replacing the `requests`-based HTTP calls in the `HackerNews` class with equivalent `pycurl` calls.
2. Using `pycurl.Curl` to perform HTTP GET requests.
3. Capturing the response data using a `BytesIO` buffer, as `pycurl` writes directly to a file-like object.
4. Handling errors explicitly, as `pycurl` does not raise exceptions like `requests`.

Below is the modified code with the necessary changes.

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck
"""

import unittest
import pycurl
from io import BytesIO
import json


class HackerNews:
    def __init__(self):
        pass

    def _run_async(self, urls):
        responses = []
        for url in urls:
            buffer = BytesIO()
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEDATA, buffer)
            try:
                curl.perform()
                status_code = curl.getinfo(pycurl.RESPONSE_CODE)
                if status_code == 200:
                    body = buffer.getvalue().decode('utf-8')
                    responses.append(json.loads(body))
                else:
                    responses.append(None)
            except pycurl.error:
                responses.append(None)
            finally:
                curl.close()
                buffer.close()
        return responses


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_async(self):
        response = self.hn._run_async([self.url])
        self.assertEqual(response[0]['id'], 8863)
        self.assertEqual(response[0]['by'], 'dhouston')

    def test_get_async_error(self):
        response = self.hn._run_async([self.err_url])
        self.assertEqual(response, [None])

    def tearDown(self):
        pass  # No session to close in pycurl


if __name__ == '__main__':
    unittest.main()
```

---

### Key Changes:
1. **Replaced `requests` with `pycurl`**:
   - The `HackerNews` class now uses `pycurl.Curl` to perform HTTP GET requests.
   - A `BytesIO` buffer is used to capture the response body, as `pycurl` writes directly to a file-like object.

2. **Error Handling**:
   - Explicitly handled errors using `pycurl.error` to append `None` to the responses list when a request fails.

3. **Session Management**:
   - Removed the `self.hn.session.close()` call in `tearDown`, as `pycurl` does not use persistent sessions like `requests`.

4. **Response Parsing**:
   - Decoded the response from the `BytesIO` buffer and parsed it using `json.loads`.

This ensures the functionality remains consistent while using `pycurl` instead of `requests`.