#!/usr/bin/env python

"""
Tests get_all()

@author john keck
@email robertjkeck
"""

import unittest
import urllib3

from hackernews import HackerNews
from hackernews import Item


class TestGetLast(unittest.TestCase):

    def setUp(self):
        # Initialize HackerNews with urllib3's PoolManager
        self.hn = HackerNews()
        self.hn.session = urllib3.PoolManager()

    def test_get_item(self):
        items = self.hn.get_last(5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 5)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        # Properly clean up the PoolManager
        self.hn.session.clear()

if __name__ == '__main__':
    unittest.main()
