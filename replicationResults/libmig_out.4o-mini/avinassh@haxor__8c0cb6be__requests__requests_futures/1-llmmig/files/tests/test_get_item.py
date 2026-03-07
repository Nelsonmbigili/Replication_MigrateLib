#!/usr/bin/env python

"""
Tests get_item()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
from requests_futures.sessions import FuturesSession  # Changed import

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidItemID


class TestGetItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.hn.session = FuturesSession()  # Changed to FuturesSession

    def test_get_item(self):
        future = self.hn.get_item(8863)  # Assuming get_item uses session to make a request
        item = future.result()  # Get the result from the future
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
        future = self.hn.get_item(8863, expand=True)  # Assuming get_item uses session to make a request
        item = future.result()  # Get the result from the future
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertIsInstance(item.by, User)
        self.assertIsInstance(item.kids[0], Item)

    def tearDown(self):
        self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
