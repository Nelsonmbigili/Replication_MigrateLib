#!/usr/bin/env python

"""
Tests top_stories()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
import urllib3
import json

from hackernews import HackerNews
from hackernews import Item


class TestTopStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = urllib3.PoolManager()

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
        self.hn.session.clear()  # Clear the session instead of closing

if __name__ == '__main__':
    unittest.main()
