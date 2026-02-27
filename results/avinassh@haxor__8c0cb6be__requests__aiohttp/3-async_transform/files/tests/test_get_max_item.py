#!/usr/bin/env python

"""
Tests get_max_item()

@author avinash sajjanshetty
@email a@sajjanshetty
"""

import unittest
from hackernews import HackerNews
from hackernews import Item
import pytest


class TestGetMaxItem(unittest.IsolatedAsyncioTestCase):  # Use IsolatedAsyncioTestCase for async tests

    async def asyncSetUp(self):
        self.hn = HackerNews()

    @pytest.mark.asyncio
    async def test_get_max_item(self):
        max_item_id = await self.hn.get_max_item()  # Await the async method
        self.assertIsInstance(max_item_id, int)

    @pytest.mark.asyncio
    async def test_get_max_item_expand(self):
        max_item = await self.hn.get_max_item(expand=True)  # Await the async method
        self.assertIsInstance(max_item, Item)

    async def asyncTearDown(self):
        await self.hn.session.close()  # Close the aiohttp session asynchronously

if __name__ == '__main__':
    unittest.main()
