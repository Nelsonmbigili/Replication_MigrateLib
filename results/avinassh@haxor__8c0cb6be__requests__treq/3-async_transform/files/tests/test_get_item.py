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
import pytest


class TestGetItem(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()

    @pytest.mark.asyncio
    async def test_get_item(self):
        item = await self.hn.get_item(8863)  # Await the asynchronous call
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertEqual(item.by, "dhouston")
        self.assertEqual(
            repr(item),
            ('<hackernews.Item: 8863 - My YC app: '
                'Dropbox - Throw away your USB drive>')
        )

    async def test_invalid_item(self):
        with self.assertRaises(InvalidItemID):
            await self.hn.get_item(0)  # Await the asynchronous call

    @pytest.mark.asyncio
    async def test_get_item_expand(self):
        item = await self.hn.get_item(8863, expand=True)  # Await the asynchronous call
        self.assertIsInstance(item, Item)
        self.assertEqual(item.item_id, 8863)
        self.assertIsInstance(item.by, User)
        self.assertIsInstance(item.kids[0], Item)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Close the session asynchronously

if __name__ == '__main__':
    unittest.main()
