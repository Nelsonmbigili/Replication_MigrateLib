#!/usr/bin/env python

"""
Tests show_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession  # Importing FuturesSession

from hackernews import HackerNews
from hackernews import Item


class TestShowStories(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Using FuturesSession instead of requests.Session

    def test_show_stories(self):
        future = self.hn.show_stories(limit=10)  # Assuming show_stories returns a future
        show_stories = future.result()  # Getting the result from the future
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], Item)
        self.assertIsNotNone(show_stories)

    def test_show_stories_raw(self):
        future = self.hn.show_stories(raw=True)  # Assuming show_stories returns a future
        show_stories = future.result()  # Getting the result from the future
        self.assertIsInstance(show_stories, list)
        self.assertIsInstance(show_stories[0], str)
        self.assertIsNotNone(show_stories)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
