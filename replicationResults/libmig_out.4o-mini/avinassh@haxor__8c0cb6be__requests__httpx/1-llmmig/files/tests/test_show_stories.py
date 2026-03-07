#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import httpx  # Added import for httpx

from hackernews import HackerNews
from hackernews import Item


class TestShowStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = httpx.Client()  # Changed to use httpx.Client()

    def test_show_stories(self):
        show_stories = self.hn.show_stories(limit=10)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    def test_show_stories_raw(self):
        show_stories = self.hn.show_stories(raw=True)
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    def tearDown(self):
        self.hn.session.close()  # No change needed here

if __name__ == '__main__':
    unittest.main()
