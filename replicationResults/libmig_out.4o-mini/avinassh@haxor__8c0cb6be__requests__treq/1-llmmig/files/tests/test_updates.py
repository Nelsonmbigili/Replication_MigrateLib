#!/usr/bin/env python

"""
Tests updates()

@author avinash sajjanshetty
@email hi@avi.im
"""

import unittest
import treq  # Changed from requests to treq

from hackernews import HackerNews


class TestUpdates(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_top_stories(self):
        updates = self.hn.updates()
        self.assertIsNotNone(updates)
        self.assertIsInstance(updates, dict)
        self.assertIsInstance(updates['profiles'], list)
        self.assertIsInstance(updates['items'], list)

    def tearDown(self):
        # Removed self.hn.session.close() as treq does not require explicit session closure
        pass

if __name__ == '__main__':
    unittest.main()
