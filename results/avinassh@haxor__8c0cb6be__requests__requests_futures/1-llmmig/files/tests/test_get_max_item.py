#!/usr/bin/env python

"""
Tests get_max_item()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
from requests_futures.sessions import FuturesSession  # Import FuturesSession
from hackernews import HackerNews
from hackernews import Item


class TestGetMaxItem(unittest.TestCase):

    def setUp(self):
        # Replace the session in HackerNews with a FuturesSession
        self.hn = HackerNews()
        self.hn.session = FuturesSession()

    def test_get_max_item(self):
        max_item_id = self.hn.get_max_item()
        self.assertIsInstance(max_item_id, int)

    def test_get_max_item_expand(self):
        max_item = self.hn.get_max_item(expand=True)
        self.assertIsInstance(max_item, Item)

    def tearDown(self):
        # Close the FuturesSession
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
