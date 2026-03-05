#!/usr/bin/env python

"""
Tests get_all()

@author john keck
@email robertjkeck2@gmail.com
"""

import unittest
import treq  # Importing treq instead of requests

from hackernews import HackerNews
from hackernews import Item


class TestGetLast(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        items = self.hn.get_last(5)
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 5)
        self.assertIsInstance(items[0], Item)

    def tearDown(self):
        # No need to close a session in treq
        pass

if __name__ == '__main__':
    unittest.main()
