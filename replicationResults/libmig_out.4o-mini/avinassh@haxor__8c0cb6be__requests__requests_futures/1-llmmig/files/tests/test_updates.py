#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
from requests_futures.sessions import FuturesSession
from hackernews import HackerNews


class TestUpdates(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Change to FuturesSession

    def test_top_stories(self):
        updates_future = self.hn.updates()  # This will return a future
        updates = updates_future.result()  # Get the result from the future
        self.assertIsNotNone(updates)
        self.assertIsInstance(updates, dict)
        self.assertIsInstance(updates['profiles'], list)
        self.assertIsInstance(updates['items'], list)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
