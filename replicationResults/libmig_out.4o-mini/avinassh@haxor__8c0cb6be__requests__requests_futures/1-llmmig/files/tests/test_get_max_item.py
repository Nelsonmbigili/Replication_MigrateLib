#!/usr/bin/env python

"""
Tests get_max_item()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
from requests_futures.sessions import FuturesSession  # Importing FuturesSession

from hackernews import HackerNews
from hackernews import Item


class TestGetMaxItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Using FuturesSession instead of requests.Session

    def test_get_max_item(self):
        max_item_id = self.hn.get_max_item()
        self.assertIsInstance(max_item_id, int)

    def test_get_max_item_expand(self):
        max_item = self.hn.get_max_item(expand=True)
        self.assertIsInstance(max_item, Item)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
