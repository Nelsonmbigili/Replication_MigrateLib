#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
@email robertjke
"""

import unittest
import urllib3
import json

from hackernews import Item


class HackerNews:
    """
    Mocked HackerNews class for demonstration purposes.
    Migrated to use urllib3 instead of requests.
    """
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        self.session = urllib3.PoolManager()

    def get_items_by_ids(self, ids, item_type=None):
        items = []
        for item_id in ids:
            url = f"{self.BASE_URL}/item/{item_id}.json"
            response = self.session.request("GET", url)
            if response.status == 200:
                item_data = json.loads(response.data.decode("utf-8"))
                if item_type is None or item_data.get("type") == item_type:
                    items.append(Item(item_data))
        return items

    def close(self):
        self.session.clear()


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
