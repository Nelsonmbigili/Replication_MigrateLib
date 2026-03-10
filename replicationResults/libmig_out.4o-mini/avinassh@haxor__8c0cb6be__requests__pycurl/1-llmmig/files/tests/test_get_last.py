#!/usr/bin/env python

"""
Tests get_all()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import pycurl
from io import BytesIO
from hackernews import HackerNews
from hackernews import Item


class TestGetLast(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        items = self.hn.get_last(5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 5)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        pass  # No session to close in pycurl

# Assuming the get_last method in HackerNews is modified to use pycurl
def get_last(self, count):
    url = f"https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    
    response = buffer.getvalue()
    # Assuming the response is JSON and needs to be parsed
    items_ids = json.loads(response)
    # Fetch the items based on the IDs
    items = [self.get_item(item_id) for item_id in items_ids[:count]]
    return items

if __name__ == '__main__':
    unittest.main()
