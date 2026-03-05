#!/usr/bin/env python

"""
Tests get_max_item()

@author avinash sajjanshetty
@email a@sajjanshetty.com
"""

import unittest
import aiohttp
import asyncio

from hackernews import HackerNews
from hackernews import Item


class TestGetMaxItem(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()

    async def async_get_max_item(self):
        return await self.hn.get_max_item()

    async def async_get_max_item_expand(self):
        return await self.hn.get_max_item(expand=True)

    def test_get_max_item(self):
        max_item_id = asyncio.run(self.async_get_max_item())
        self.assertIsInstance(max_item_id, int)

    def test_get_max_item_expand(self):
        max_item = asyncio.run(self.async_get_max_item_expand())
        self.assertIsInstance(max_item, Item)

    def tearDown(self):
        asyncio.run(self.hn.session.close())

if __name__ == '__main__':
    unittest.main()
