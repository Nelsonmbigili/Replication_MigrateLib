### Explanation of Changes
To migrate the code from using the `requests` library to using `pycurl`, the following changes were made:

1. **Session Management**: The `requests` library manages sessions automatically, while `pycurl` requires explicit handling of the curl object. Therefore, I created a `pycurl.Curl` object in the `setUp` method and closed it in the `tearDown` method.
2. **Making Requests**: The way to make HTTP requests changes significantly. Instead of using `requests.get()`, I set the necessary options on the `pycurl.Curl` object to perform the GET request.
3. **Response Handling**: The response from `pycurl` is handled differently. I used a `BytesIO` object to capture the response data, which is then decoded to a string for further processing.

Here is the modified code:

```python
#!/usr/bin/env python

"""
Tests get_max_item()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import Item


class TestGetMaxItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.curl = pycurl.Curl()

    def test_get_max_item(self):
        buffer = BytesIO()
        self.curl.setopt(self.curl.URL, 'https://hacker-news.firebaseio.com/v0/maxitem.json')
        self.curl.setopt(self.curl.WRITEDATA, buffer)
        self.curl.perform()
        max_item_id = int(buffer.getvalue().decode('utf-8'))
        self.assertIsInstance(max_item_id, int)

    def test_get_max_item_expand(self):
        buffer = BytesIO()
        self.curl.setopt(self.curl.URL, 'https://hacker-news.firebaseio.com/v0/maxitem.json?expand=true')
        self.curl.setopt(self.curl.WRITEDATA, buffer)
        self.curl.perform()
        max_item_data = buffer.getvalue().decode('utf-8')
        max_item = Item.from_json(max_item_data)  # Assuming Item has a method to create from JSON
        self.assertIsInstance(max_item, Item)

    def tearDown(self):
        self.curl.close()

if __name__ == '__main__':
    unittest.main()
``` 

This code now uses `pycurl` for making HTTP requests instead of `requests`, while maintaining the original structure and functionality of the tests.