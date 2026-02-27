#!/usr/bin/env python

"""
Tests get_max_item()

@author avinash sajjanshetty
"""

import unittest
import urllib3
from hackernews import Item


class HackerNews:
    """
    Mock implementation of the HackerNews class to demonstrate migration to urllib3.
    Replace this with the actual implementation of the HackerNews class.
    """

    def __init__(self):
        self.http = urllib3.PoolManager()

    def get_max_item(self, expand=False):
        # Example API endpoint for Hacker News max item
        url = "https://hacker-news.firebaseio.com/v0/maxitem.json"
        response = self.http.request("GET", url)
        if response.status == 200:
            max_item_id = int(response.data.decode("utf-8"))
            if expand:
                return self.get_item(max_item_id)
            return max_item_id
        else:
            raise Exception(f"Failed to fetch max item. HTTP status: {response.status}")

    def get_item(self, item_id):
        # Example API endpoint for fetching an item
        url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        response = self.http.request("GET", url)
        if response.status == 200:
            item_data = response.data.decode("utf-8")
            return Item(item_data)  # Assuming Item is a class that processes item data
        else:
            raise Exception(f"Failed to fetch item {item_id}. HTTP status: {response.status}")

    def close(self):
        self.http.clear()  # Cleanup the PoolManager


class TestGetMaxItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_max_item(self):
        max_item_id = self.hn.get_max_item()
        self.assertIsInstance(max_item_id, int)

    def test_get_max_item_expand(self):
        max_item = self.hn.get_max_item(expand=True)
        self.assertIsInstance(max_item, Item)

    def tearDown(self):
        self.hn.close()


if __name__ == '__main__':
    unittest.main()
