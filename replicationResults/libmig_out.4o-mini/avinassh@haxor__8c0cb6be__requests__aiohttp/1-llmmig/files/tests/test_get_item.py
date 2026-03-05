#!/usr/bin/env python

"""
Tests get_item()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
import asyncio

from hackernews import HackerNews
from hackernews import Item, User
from hackernews import InvalidItemID


class TestGetItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    async def async_test_get_item(self):
        item = await self.hn.get_item(8863)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertEqual(item.by, "dhouston")
        self.assertEqual(
            repr(item),
            ('<hackernews.Item: 8863 - My YC app: '
                'Dropbox - Throw away your USB drive>')
        )

    async def async_test_invalid_item(self):
        self.assertRaises(InvalidItemID, await self.hn.get_item, 0)

    async def async_test_get_item_expand(self):
        item = await self.hn.get_item(8863, expand=True)
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertIsInstance(item.by, User)
        self.assertIsInstance(item.kids[0], Item)

    def tearDown(self):
        self.hn.session.close()

    def test_get_item(self):
        asyncio.run(self.async_test_get_item())

    def test_invalid_item(self):
        asyncio.run(self.async_test_invalid_item())

    def test_get_item_expand(self):
        asyncio.run(self.async_test_get_item_expand())

if __name__ == '__main__':
    unittest.main()
