#!/usr/bin/env python

"""
Tests get_max_item()

@author avinash sajjanshetty
"""

import unittest

from hackernews import HackerNews
from hackernews import Item


class TestGetMaxItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_max_item(self):
        max_item_id = self.hn.get_max_item()
        self.assertIsInstance(max_item_id, int)

    def test_get_max_item_expand(self):
        max_item = self.hn.get_max_item(expand=True)
        self.assertIsInstance(max_item, Item)

    def tearDown(self):
        # Assuming the HackerNews class now uses pycurl, ensure any cleanup is handled here.
        self.hn.close()  # Updated to call a close method for pycurl cleanup.

if __name__ == '__main__':
    unittest.main()
