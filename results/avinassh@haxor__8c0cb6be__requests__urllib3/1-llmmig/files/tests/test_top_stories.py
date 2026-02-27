#!/usr/bin/env python

"""
Tests top_stories()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
import urllib3
import json

from hackernews import Item


class HackerNews:
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.session = urllib3.PoolManager()

    def top_stories(self, limit=None, raw=False):
        url = f"{self.base_url}/topstories.json"
        response = self.session.request("GET", url)
        response_data = json.loads(response.data.decode("utf-8"))

        if limit:
            response_data = response_data[:limit]

        if raw:
            return [str(item_id) for item_id in response_data]

        return [Item(item_id) for item_id in response_data]


class TestTopStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_top_stories(self):
        top_stories = self.hn.top_stories(limit=10)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], Item)
        self.assertIsNotNone(top_stories)

    def test_top_stories_raw(self):
        top_stories = self.hn.top_stories(raw=True)
        self.assertIsInstance(top_stories, list)
        self.assertIsInstance(top_stories[0], str)
        self.assertIsNotNone(top_stories)

    def tearDown(self):
        self.hn.session.clear()  # Properly close the PoolManager


if __name__ == '__main__':
    unittest.main()
