#!/usr/bin/env python

"""
Tests get_item()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidItemID
from requests_futures.sessions import FuturesSession  # Import FuturesSession


class TestGetItem(unittest.TestCase):

    def setUp(self):
        # Replace the session in HackerNews with a FuturesSession
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Use FuturesSession for async requests

    def test_get_item(self):
        item = self.hn.get_item(8863)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertEqual(item.by, "dhouston")
        self.assertEqual(
            repr(item),
            ('<hackernews.Item: 8863 - My YC app: '
                'Dropbox - Throw away your USB drive>')
        )

    def test_invalid_item(self):
        self.assertRaises(InvalidItemID, self.hn.get_item, 0)

    def test_get_item_expand(self):
        item = self.hn.get_item(8863, expand=True)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertIsInstance(item.by, User)
        self.assertIsInstance(item.kids[0], Item)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
