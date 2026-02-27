#!/usr/bin/env python

"""
Tests get_items_by_ids()

@author john keck
"""

import unittest
import asyncio

from hackernews import HackerNews
from hackernews import Item
import pytest


class TestGetItemsByIDs(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.hn = HackerNews()

    @pytest.mark.asyncio
    async def test_get_items_by_ids(self):
        items = await self.hn.get_items_by_ids([1, 2, 3])
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 3)
        self.assertIsInstance(items[0], Item)

    @pytest.mark.asyncio
    async def test_get_items_by_ids_filtered(self):
        items = await self.hn.get_items_by_ids(
            [i for i in range(1, 50)],
            item_type='story'
        )
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 37)
        self.assertIsInstance(items[0], Item)

    async def asyncTearDown(self):
        await self.hn.session.close()

if __name__ == '__main__':
    unittest.main()
