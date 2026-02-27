#!/usr/bin/env python

"""
Tests new_stories()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession  # Import FuturesSession
from hackernews import HackerNews
from hackernews import Item


class TestNewStories(unittest.TestCase):

    def setUp(self):
        # Assuming HackerNews accepts a session object, we pass a FuturesSession instance
        self.hn = HackerNews(session=FuturesSession())

    def test_new_stories(self):
        new_stories = self.hn.new_stories(limit=10)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], Item)
        self.assertIsNotNone(new_stories)

    def test_new_stories_raw(self):
        new_stories = self.hn.new_stories(raw=True)
        self.assertIsInstance(new_stories, list)
        self.assertIsInstance(new_stories[0], str)
        self.assertIsNotNone(new_stories)

    def tearDown(self):
        self.hn.session.close()  # Close the FuturesSession

if __name__ == '__main__':
    unittest.main()
