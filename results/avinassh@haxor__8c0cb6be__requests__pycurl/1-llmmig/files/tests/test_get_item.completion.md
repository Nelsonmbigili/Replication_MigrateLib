### Explanation of Changes:
The original code uses the `requests` library for HTTP requests, but we are migrating it to use the `pycurl` library. Since `pycurl` operates at a lower level than `requests`, it requires more explicit handling of HTTP requests and responses. The changes include:
1. Replacing `requests`-based HTTP calls in the `HackerNews` class with equivalent `pycurl` calls.
2. Using `pycurl.Curl` to set up the HTTP request, configure options (e.g., URL, headers), and capture the response.
3. Using a `BytesIO` object to store the response body, as `pycurl` writes directly to a file-like object.
4. Ensuring proper cleanup of `pycurl.Curl` objects to avoid resource leaks.

Below is the modified code with the necessary changes.

---

### Modified Code:
```python
#!/usr/bin/env python

"""
Tests get_item()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
import pycurl
from io import BytesIO
import json

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidItemID


class HackerNews:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        pass

    def _make_request(self, endpoint):
        """
        Makes an HTTP GET request to the given endpoint using pycurl.
        """
        url = f"{self.BASE_URL}/{endpoint}.json"
        buffer = BytesIO()
        curl = pycurl.Curl()
        try:
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            curl.setopt(pycurl.FOLLOWLOCATION, True)
            curl.setopt(pycurl.USERAGENT, "pycurl/7.45.6")
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            if status_code != 200:
                raise InvalidItemID(f"Invalid response code: {status_code}")
        finally:
            curl.close()

        response_body = buffer.getvalue().decode("utf-8")
        return json.loads(response_body)

    def get_item(self, item_id, expand=False):
        """
        Fetches an item by its ID.
        """
        endpoint = f"item/{item_id}"
        data = self._make_request(endpoint)

        if not data:
            raise InvalidItemID(f"Item with ID {item_id} does not exist.")

        item = Item(data)
        if expand and "kids" in data:
            item.kids = [self.get_item(kid_id) for kid_id in data["kids"]]
        return item


class TestGetItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        item = self.hn.get_item(8863)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertEqual(item.by, "dhouston")
        self.assertEqual(
            repr(item),
            ('<hackernews.Item: 8863 - My YC app: '
                'Dropbox - Throw away your USB drive>')
        )

    def test_invalid_item(self):
        self.assertRaises(InvalidItemID, self.hn.get_item, 0)

    def test_get_item_expand(self):
        item = self.hn.get_item(8863, expand=True)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertIsInstance(item.by, User)
        self.assertIsInstance(item.kids[0], Item)

    def tearDown(self):
        pass  # No session to close with pycurl


if __name__ == '__main__':
    unittest.main()
```

---

### Key Changes:
1. **Replaced `requests` with `pycurl`**:
   - The `_make_request` method now uses `pycurl.Curl` to perform HTTP GET requests.
   - A `BytesIO` object is used to capture the response body, which is then decoded and parsed as JSON.

2. **Error Handling**:
   - If the HTTP response code is not `200`, an `InvalidItemID` exception is raised.

3. **Session Management**:
   - Since `pycurl` does not use persistent sessions like `requests.Session`, the `tearDown` method no longer closes a session.

4. **Dependencies**:
   - The `pycurl` library and `io.BytesIO` are used for HTTP requests and response handling.

This code maintains the original functionality while replacing `requests` with `pycurl`.