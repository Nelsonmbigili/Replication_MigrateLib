#!/usr/bin/env python

"""
Tests get_item()

@author avinash sajjanshetty
"""

import unittest
import asyncio

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidItemID


class TestGetItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    def test_get_item(self):
        async def run_test():
            item = await self.hn.get_item(8863)
            self.assertIsInstance(item, Item)
            self.assertEqual(item.item_id, 8863)
            self.assertEqual(item.by, "dhouston")
            self.assertEqual(
                repr(item),
                ('<hackernews.Item: 8863 - My YC app: '
                    'Dropbox - Throw away your USB drive>')
            )
        asyncio.run(run_test())

    def test_invalid_item(self):
        async def run_test():
            with self.assertRaises(InvalidItemID):
                await self.hn.get_item(0)
        asyncio.run(run_test())

    def test_get_item_expand(self):
        async def run_test():
            item = await self.hn.get_item(8863, expand=True)
            self.assertIsInstance(item, Item)
            self.assertEqual(item.item_id, 8863)
            self.assertIsInstance(item.by, User)
            self.assertIsInstance(item.kids[0], Item)
        asyncio.run(run_test())

    def tearDown(self):
        asyncio.run(self.hn.session.close())

if __name__ == '__main__':
    unittest.main()
