#!/usr/bin/env python

"""
Tests ask_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession  # Changed import

from hackernews import HackerNews
from hackernews import Item


class TestAskStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Changed to FuturesSession

    def test_ask_stories(self):
        future = self.hn.ask_stories(limit=10)
        ask_stories = future.result()  # Get the result from the future
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], Item)
        self.assertIsNotNone(ask_stories)

    def test_ask_stories_raw(self):
        future = self.hn.ask_stories(raw=True)
        ask_stories = future.result()  # Get the result from the future
        self.assertIsInstance(ask_stories, list)
        self.assertIsInstance(ask_stories[0], str)
        self.assertIsNotNone(ask_stories)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
