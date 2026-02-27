#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjke
"""

import unittest
import pycurl
from io import BytesIO
import json


class Item:
    """Represents a Hacker News item."""
    def __init__(self, item_id, item_type=None):
        self.id = item_id
        self.type = item_type


class HackerNews:
    """Hacker News API client using pycurl."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.curl = pycurl.Curl()

    def _make_request(self, endpoint):
        """Helper method to make an HTTP GET request using pycurl."""
        url = f"{self.BASE_URL}/{endpoint}.json"
        buffer = BytesIO()

        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        self.curl.setopt(pycurl.FOLLOWLOCATION, True)
        self.curl.setopt(pycurl.TIMEOUT, 10)

        self.curl.perform()
        status_code = self.curl.getinfo(pycurl.RESPONSE_CODE)

        if status_code != 200:
            raise Exception(f"HTTP request failed with status code {status_code}")

        response_data = buffer.getvalue().decode('utf-8')
        return json.loads(response_data)

    def get_items_by_ids(self, ids, item_type=None):
        """Fetch multiple items by their IDs."""
        items = []
        for item_id in ids:
            data = self._make_request(f"item/{item_id}")
            if item_type is None or data.get("type") == item_type:
                items.append(Item(item_id, data.get("type")))
        return items

    def close(self):
        """Clean up the pycurl object."""
        self.curl.close()


class TestGetItemsByIDs(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_items_by_ids(self):
        items = self.hn.get_items_by_ids([1, 2, 3])
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 3)
        self.assertIsInstance(items[0], Item)

    def test_get_items_by_ids_filtered(self):
        items = self.hn.get_items_by_ids(
            [i for i in range(1, 50)],
            item_type='story'
        )
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 37)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        self.hn.close()


if __name__ == '__main__':
    unittest.main()
