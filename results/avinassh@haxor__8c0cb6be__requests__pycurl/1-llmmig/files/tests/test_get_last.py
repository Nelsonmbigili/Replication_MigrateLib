#!/usr/bin/env python

"""
Tests get_all()

@author john keck
@email robertjkeck
"""

import unittest
import pycurl
import json
from io import BytesIO


class Item:
    """Represents a Hacker News item."""
    def __init__(self, item_id, title, url):
        self.item_id = item_id
        self.title = title
        self.url = url


class HackerNews:
    """A simple client for the Hacker News API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self):
        pass

    def get_last(self, count):
        """
        Fetch the last `count` items from the Hacker News API.
        """
        items = []
        for i in range(count):
            item_id = self._get_max_item_id() - i
            item_data = self._get_item(item_id)
            items.append(Item(item_id, item_data.get("title"), item_data.get("url")))
        return items

    def _get_max_item_id(self):
        """
        Fetch the maximum item ID from the Hacker News API.
        """
        url = f"{self.BASE_URL}/maxitem.json"
        response = self._make_request(url)
        return int(response)

    def _get_item(self, item_id):
        """
        Fetch an item by its ID from the Hacker News API.
        """
        url = f"{self.BASE_URL}/item/{item_id}.json"
        response = self._make_request(url)
        return json.loads(response)

    def _make_request(self, url):
        """
        Make an HTTP GET request using pycurl and return the response body as a string.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEDATA, buffer)
        curl.setopt(curl.FOLLOWLOCATION, True)
        curl.setopt(curl.USERAGENT, "HackerNewsClient/1.0")
        curl.perform()
        curl.close()
        return buffer.getvalue().decode("utf-8")


class TestGetLast(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        items = self.hn.get_last(5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 5)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        pass  # No session to close since pycurl does not use persistent sessions.


if __name__ == '__main__':
    unittest.main()
