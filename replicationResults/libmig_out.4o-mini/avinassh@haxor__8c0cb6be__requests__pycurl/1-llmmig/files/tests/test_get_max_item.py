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
